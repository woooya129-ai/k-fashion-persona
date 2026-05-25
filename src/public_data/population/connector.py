# SPDX-License-Identifier: AGPL-3.0-only
"""MOIS resident-registration population connector and snapshot fallback.

The context is aggregate public statistics only. It is used to describe the
selected synthetic panel, not to infer individual purchasing power or demand.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from src.public_data import DataGoKrAuthAdapter, PublicDataCache

REPO_ROOT = Path(__file__).resolve().parents[3]
MOIS_POPULATION_SNAPSHOT_PATH = REPO_ROOT / "data" / "public" / "mois_population_context.csv"
MOIS_POPULATION_SOURCE_URL = "https://jumin.mois.go.kr/agePpltStus.do"
MOIS_POPULATION_DATA_GO_KR_URL = "https://www.data.go.kr/data/15108072/openapi.do"
DATAGOKR_SERVICE_KEY_VAR = "DATAGOKR_SERVICE_KEY"
MOIS_POPULATION_API_URL_VAR = "MOIS_POPULATION_API_URL"

_ALLOWED_API_HOSTS = frozenset({"apis.data.go.kr"})
_ALLOWED_API_PATH_PREFIXES = ("/1741000/", "/15108072/")
_SOURCE_NAME = "MOIS resident registration population"
_SCOPE_NOTE = (
    "MOIS 주민등록 인구는 주민등록 기준 집계 통계입니다. 거주자, 거주불명자, "
    "재외국민을 포함하고 외국인은 제외합니다."
)
_MARGINAL_NOTE = (
    "MOIS 비교값은 성별, 연령, 지역을 모두 교차한 값이 아니라 선택 지역 기준 "
    "연령 버킷/성별/지역 주변분포입니다."
)
_AGE_BUCKETS: tuple[tuple[str, int, int], ...] = (
    ("0-9", 0, 9),
    ("10-19", 10, 19),
    ("20-29", 20, 29),
    ("30-39", 30, 39),
    ("40-49", 40, 49),
    ("50-59", 50, 59),
    ("60-69", 60, 69),
    ("70-79", 70, 79),
    ("80-89", 80, 89),
    ("90-99", 90, 99),
    ("100+", 100, 200),
)

_PROVINCE_ALIASES: dict[str, str] = {
    "전국": "전국",
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
}

_REGION_KEYS = (
    "region_label",
    "region",
    "name",
    "sido",
    "시도명",
    "행정기관",
    "행정기관명",
    "법정동",
)
_TOTAL_KEYS = ("total", "total_population", "totPopltn", "총인구수", "계")
_MALE_KEYS = ("male", "male_population", "malePopltn", "남자인구수", "남자")
_FEMALE_KEYS = ("female", "female_population", "femalePopltn", "여자인구수", "여자")
_PERIOD_KEYS = ("period", "statsYm", "통계년월", "기준년월")


@dataclass(frozen=True)
class PopulationRow:
    region_label: str
    period: str
    total: int
    male: int
    female: int
    age_counts: dict[str, int]
    source_name: str = _SOURCE_NAME
    source_url: str = MOIS_POPULATION_SOURCE_URL
    unit: str = "persons"


def _parse_int(value: Any) -> int:
    text = str(value or "").replace(",", "").strip()
    if not text or text in {"-", "null", "None"}:
        return 0
    return int(float(text))


def _first_value(row: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def _normalize_region_label(label: str) -> str:
    text = str(label).strip()
    return _PROVINCE_ALIASES.get(text, text)


def _canonical_region_label(row: dict[str, Any]) -> str:
    sido = str(row.get("시도명") or row.get("ctpvNm") or "").strip()
    sigungu = str(row.get("시군구명") or row.get("sggNm") or "").strip()
    eupmyeondong = str(row.get("행정동명") or row.get("emdNm") or row.get("법정동명") or "").strip()
    if sido:
        parts = [sido, sigungu, eupmyeondong]
        return " ".join(part for part in parts if part)
    return _normalize_region_label(str(_first_value(row, _REGION_KEYS)))


def _age_value(row: dict[str, Any], bucket: str) -> int:
    if bucket.endswith("+"):
        korean_bucket = f"만{bucket.rstrip('+')}세이상"
    else:
        start, end = bucket.split("-", maxsplit=1)
        korean_bucket = f"만{start}~{end}세"
    normalized = bucket.replace("+", "세이상")
    candidates = (
        f"age_{bucket}",
        f"age_{bucket.replace('-', '_').replace('+', '_plus')}",
        f"{bucket}세",
        korean_bucket,
        f"연령_{bucket}",
        f"만{normalized}",
    )
    for key in candidates:
        if key in row:
            return _parse_int(row[key])

    male_candidates = (
        f"male_{bucket}",
        f"남자_{bucket}",
        f"{korean_bucket}남자",
        f"만{normalized}남자",
    )
    female_candidates = (
        f"female_{bucket}",
        f"여자_{bucket}",
        f"{korean_bucket}여자",
        f"만{normalized}여자",
    )
    male = next((_parse_int(row[key]) for key in male_candidates if key in row), 0)
    female = next((_parse_int(row[key]) for key in female_candidates if key in row), 0)
    return male + female


def _period_from_row(row: dict[str, Any], default: str = "") -> str:
    period = str(_first_value(row, _PERIOD_KEYS)).strip()
    if len(period) == 6 and period.isdigit():
        return f"{period[:4]}-{period[4:]}"
    return period or default


def _province_group_label(row: dict[str, Any]) -> str:
    label = str(row.get("시도명") or row.get("ctpvNm") or "").strip()
    return _normalize_region_label(label)


def _row_from_dict(
    row: dict[str, Any],
    *,
    default_period: str = "",
    region_label_override: str = "",
) -> PopulationRow:
    region_label = region_label_override or _canonical_region_label(row)
    total = _parse_int(_first_value(row, _TOTAL_KEYS))
    male = _parse_int(_first_value(row, _MALE_KEYS))
    female = _parse_int(_first_value(row, _FEMALE_KEYS))
    age_counts = {bucket: _age_value(row, bucket) for bucket, _, _ in _AGE_BUCKETS}
    if not total:
        total = sum(age_counts.values()) or male + female
    return PopulationRow(
        region_label=region_label,
        period=_period_from_row(row, default_period),
        total=total,
        male=male,
        female=female,
        age_counts=age_counts,
        source_name=str(row.get("source_name") or _SOURCE_NAME),
        source_url=str(row.get("source_url") or MOIS_POPULATION_SOURCE_URL),
        unit=str(row.get("unit") or "persons"),
    )


def load_population_snapshot(path: Path = MOIS_POPULATION_SNAPSHOT_PATH) -> list[PopulationRow]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        return [_row_from_dict(dict(row)) for row in csv.DictReader(fh)]


def _extract_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []

    candidates: list[Any] = [data]
    response = data.get("response")
    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            candidates.extend([body, body.get("items")])
    candidates.extend([data.get("items"), data.get("data"), data.get("result")])

    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict):
            item = candidate.get("item")
            if isinstance(item, list):
                return [x for x in item if isinstance(x, dict)]
            if isinstance(item, dict):
                return [item]
    return []


def parse_population_api_rows(rows: list[dict[str, Any]]) -> list[PopulationRow]:
    grouped: dict[str, list[PopulationRow]] = {}
    ungrouped: list[PopulationRow] = []
    for row in rows:
        province_label = _province_group_label(row)
        parsed = _row_from_dict(row, region_label_override=province_label)
        if not parsed.region_label or parsed.total <= 0:
            continue
        if province_label:
            grouped.setdefault(province_label, []).append(parsed)
        else:
            ungrouped.append(parsed)
    return [_sum_rows(group_rows, label) for label, group_rows in grouped.items()] + ungrouped


def _validate_api_url(api_url: str) -> str:
    cleaned = api_url.strip()
    parts = urlsplit(cleaned)
    hostname = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != "https":
        raise ValueError("MOIS population API URL must use https.")
    if hostname not in _ALLOWED_API_HOSTS:
        raise ValueError(f"MOIS population API URL host is not allowed: {hostname or '<empty>'}")
    if not any(parts.path.startswith(prefix) for prefix in _ALLOWED_API_PATH_PREFIXES):
        raise ValueError("MOIS population API URL path is not allowed.")
    return cleaned


def fetch_population_api_rows(
    *,
    service_key: str,
    api_url: str,
    timeout: float = 10.0,
    params: dict[str, str] | None = None,
    cache: PublicDataCache | None = None,
) -> list[PopulationRow]:
    """Fetch and parse the configured data.go.kr MOIS population API endpoint."""
    if not service_key.strip() or not api_url.strip():
        return []
    url = _validate_api_url(api_url)
    request_params = {"pageNo": "1", "numOfRows": "1000"}
    if params:
        request_params.update(params)
    cache_key = _hash_payload({"url": url, "params": request_params})
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached
    url, request_params = DataGoKrAuthAdapter(service_key).apply(url, request_params)
    response = httpx.get(url, params=request_params, timeout=timeout)
    response.raise_for_status()
    rows = parse_population_api_rows(_extract_items(response.json()))
    if cache is not None:
        cache.set(cache_key, rows)
    return rows


def _hash_payload(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sum_rows(rows: list[PopulationRow], label: str) -> PopulationRow:
    if not rows:
        return PopulationRow(
            region_label=label,
            period="",
            total=0,
            male=0,
            female=0,
            age_counts={},
        )
    age_counts = {bucket: 0 for bucket, _, _ in _AGE_BUCKETS}
    for row in rows:
        for bucket in age_counts:
            age_counts[bucket] += int(row.age_counts.get(bucket, 0))
    periods = sorted({row.period for row in rows if row.period})
    return PopulationRow(
        region_label=label,
        period=", ".join(periods),
        total=sum(row.total for row in rows),
        male=sum(row.male for row in rows),
        female=sum(row.female for row in rows),
        age_counts=age_counts,
        source_name=rows[0].source_name,
        source_url=rows[0].source_url,
        unit=rows[0].unit,
    )


def _select_region_rows(
    rows: list[PopulationRow],
    provinces: Iterable[str],
) -> tuple[list[PopulationRow], list[str]]:
    by_label = {_normalize_region_label(row.region_label): row for row in rows}
    selected: list[PopulationRow] = []
    missing: list[str] = []
    for province in provinces:
        normalized = _normalize_region_label(str(province))
        row = by_label.get(normalized)
        if row is None:
            missing.append(str(province))
        else:
            selected.append(row)
    if selected:
        return selected, missing
    national = by_label.get("전국") or (rows[0] if rows else None)
    return ([national] if national is not None else []), missing


def _age_bucket_keys(age_min: int | None, age_max: int | None) -> list[str]:
    lo = 0 if age_min is None else max(0, int(age_min))
    hi = 200 if age_max is None else max(lo, int(age_max))
    return [bucket for bucket, start, end in _AGE_BUCKETS if end >= lo and start <= hi]


def _age_bucket_basis_label(age_keys: Iterable[str]) -> str:
    values = tuple(age_keys)
    return "all" if not values else ", ".join(values)


def _sex_population(row: PopulationRow, sex: Iterable[str]) -> tuple[str, int]:
    values = {str(value).upper() for value in sex if str(value).strip()}
    if values == {"M"}:
        return "M", row.male
    if values == {"F"}:
        return "F", row.female
    return "all", row.total


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def build_population_context(
    *,
    age_min: int | None = None,
    age_max: int | None = None,
    sex: Iterable[str] = (),
    provinces: Iterable[str] = (),
    snapshot_path: Path = MOIS_POPULATION_SNAPSHOT_PATH,
    use_api_refresh: bool = False,
    service_key: str = "",
    api_url: str = "",
    cache: PublicDataCache | None = None,
    fetch_rows_fn: Callable[..., list[PopulationRow]] = fetch_population_api_rows,
) -> dict[str, Any]:
    """Build report-only population context for the current synthetic panel filter."""
    warnings: list[str] = []
    try:
        snapshot_rows = load_population_snapshot(snapshot_path)
    except OSError as exc:
        snapshot_rows = []
        warnings.append(f"MOIS population snapshot unavailable: {type(exc).__name__}")
    rows = list(snapshot_rows)
    api_status = "snapshot"
    source_mode = "snapshot"

    if use_api_refresh:
        if not service_key.strip() or not api_url.strip():
            api_status = "missing_api_key"
            warnings.append("API 갱신 미사용, 스냅샷 사용: MOIS API key or endpoint is missing.")
        else:
            try:
                api_rows = fetch_rows_fn(
                    service_key=service_key,
                    api_url=api_url,
                    cache=cache,
                )
            except Exception as exc:  # noqa: BLE001 - report-only context must not block runs.
                api_status = "failed"
                warnings.append(f"API 갱신 실패, 스냅샷 사용: {type(exc).__name__}")
            else:
                if api_rows:
                    rows = api_rows
                    api_status = "success"
                    source_mode = "api"
                else:
                    api_status = "failed"
                    warnings.append("API 갱신 실패, 스냅샷 사용: no supported rows.")

    selected_rows, missing_regions = _select_region_rows(rows, provinces)
    selected = _sum_rows(selected_rows, " / ".join(row.region_label for row in selected_rows))
    national = _sum_rows(
        [row for row in rows if _normalize_region_label(row.region_label) == "전국"],
        "전국",
    )
    if national.total <= 0:
        national = _sum_rows(rows, "전국")

    age_keys = _age_bucket_keys(age_min, age_max)
    age_basis_label = _age_bucket_basis_label(age_keys)
    target_age_population = sum(selected.age_counts.get(key, 0) for key in age_keys)
    age_label_min = 0 if age_min is None else age_min
    age_label_max = 100 if age_max is None else age_max
    target_age_label = (
        "all" if age_min is None and age_max is None else (f"{age_label_min}-{age_label_max}")
    )
    sex_label, target_sex_population = _sex_population(selected, sex)

    if missing_regions:
        warnings.append("Some selected panel regions were not found in the population snapshot.")

    metric_rows = [
        {
            "label": "selected region population",
            "value": selected.total,
            "unit": selected.unit,
            "period": selected.period,
            "source_name": selected.source_name,
            "source_url": selected.source_url,
        },
        {
            "label": "selected age-bucket population",
            "value": target_age_population,
            "unit": selected.unit,
            "period": selected.period,
            "source_name": selected.source_name,
            "source_url": selected.source_url,
            "note": f"10-year MOIS buckets: {age_basis_label}",
        },
        {
            "label": "selected sex population",
            "value": target_sex_population,
            "unit": selected.unit,
            "period": selected.period,
            "source_name": selected.source_name,
            "source_url": selected.source_url,
            "note": "Sex marginal distribution within selected region.",
        },
    ]

    digest_rows = [
        {
            "region": row.region_label,
            "period": row.period,
            "total": row.total,
            "male": row.male,
            "female": row.female,
        }
        for row in selected_rows
    ]

    return {
        "source": "mois_population",
        "source_mode": source_mode,
        "api_status": api_status,
        "source_name": selected.source_name or _SOURCE_NAME,
        "source_url": (
            MOIS_POPULATION_DATA_GO_KR_URL if source_mode == "api" else MOIS_POPULATION_SOURCE_URL
        ),
        "period": selected.period,
        "reference_region_label": selected.region_label or "전국",
        "selected_provinces": tuple(str(value) for value in provinces),
        "missing_regions": tuple(missing_regions),
        "target_age_range": target_age_label,
        "target_age_bucket_basis": tuple(age_keys),
        "target_age_bucket_basis_label": age_basis_label,
        "target_age_population": target_age_population,
        "target_age_population_pct": _pct(target_age_population, selected.total),
        "target_sex_label": sex_label,
        "target_sex_population": target_sex_population,
        "target_sex_population_pct": _pct(target_sex_population, selected.total),
        "target_region_population": selected.total,
        "target_region_population_pct": _pct(selected.total, national.total),
        "national_population": national.total,
        "metric_rows": metric_rows,
        "population_scope_note": f"{_SCOPE_NOTE} {_MARGINAL_NOTE}",
        "warnings": tuple(warnings),
        "context_digest": _hash_payload(
            {
                "source_mode": source_mode,
                "api_status": api_status,
                "age_min": age_min,
                "age_max": age_max,
                "sex": sorted(str(value) for value in sex),
                "provinces": sorted(str(value) for value in provinces),
                "rows": digest_rows,
            }
        ),
    }
