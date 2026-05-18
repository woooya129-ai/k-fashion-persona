# SPDX-License-Identifier: AGPL-3.0-only
"""KOSIS/KOSTAT household context for price-burden prompts and reports.

Default path uses a committed snapshot for reproducibility. Optional KOSIS
statisticsData API refresh can merge user-supplied API rows without storing the
API key or relying on network access for normal operation.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
KOSIS_SNAPSHOT_PATH = REPO_ROOT / "data" / "public" / "kosis_household_context.csv"

DEFAULT_REFERENCE_SEGMENT_ID = "national_all"
DEFAULT_REFERENCE_SEGMENT_LABEL = "전국 전체"

KOSIS_API_KEY_VAR = "KOSIS_API_KEY"
KOSIS_STATISTICS_URL_VAR = "KOSIS_STATISTICS_DATA_URL"
KOSIS_STATISTICS_DATA_PATH = "/openapi/statisticsData.do"
_KOSIS_ALLOWED_HOSTS: frozenset[str] = frozenset({"kosis.kr"})

KOSTAT_2025_ANNUAL_CLOTHING_FOOTWEAR_KRW: int = 2_136_000
# Backward-compatible alias used by app/tests; value now reflects annualized
# household clothing and footwear spend from the committed KOSIS snapshot.
KOSTAT_2025_ANNUAL_CLOTHING_KRW: int = KOSTAT_2025_ANNUAL_CLOTHING_FOOTWEAR_KRW

MetricKey = Literal[
    "annualized_clothing_footwear_spend_krw",
    "monthly_clothing_footwear_spend_krw",
    "consumer_price_index_clothing_footwear",
    "online_shopping_clothing_transaction_krw",
    "online_shopping_footwear_transaction_krw",
    "online_shopping_bag_transaction_krw",
    "online_shopping_fashion_accessory_transaction_krw",
    "monthly_household_income_krw",
    "monthly_disposable_income_krw",
    "household_assets_krw",
    "household_debt_krw",
    "household_net_assets_krw",
    "annual_household_income_krw",
    "annual_disposable_income_krw",
]

REFERENCE_METRIC_LABELS: dict[str, str] = {
    "annualized_clothing_footwear_spend_krw": "연간 환산 의류·신발 지출",
    "monthly_clothing_footwear_spend_krw": "월평균 의류·신발 지출",
    "consumer_price_index_clothing_footwear": "의류·신발 소비자물가지수",
    "online_shopping_clothing_transaction_krw": "온라인쇼핑 의복 거래액",
    "online_shopping_footwear_transaction_krw": "온라인쇼핑 신발 거래액",
    "online_shopping_bag_transaction_krw": "온라인쇼핑 가방 거래액",
    "online_shopping_fashion_accessory_transaction_krw": "온라인쇼핑 패션용품 거래액",
    "monthly_household_income_krw": "월평균 가구소득",
    "monthly_disposable_income_krw": "월평균 처분가능소득",
    "household_assets_krw": "평균 가구자산",
    "household_debt_krw": "평균 가구부채",
    "household_net_assets_krw": "평균 가구순자산",
    "annual_household_income_krw": "연평균 가구소득",
    "annual_disposable_income_krw": "연평균 처분가능소득",
}

_API_METRIC_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("online_shopping_clothing_transaction_krw", ("온라인", "의복")),
    ("online_shopping_footwear_transaction_krw", ("온라인", "신발")),
    ("online_shopping_bag_transaction_krw", ("온라인", "가방")),
    ("online_shopping_fashion_accessory_transaction_krw", ("온라인", "패션")),
    ("consumer_price_index_clothing_footwear", ("소비자물가지수", "의류", "신발")),
    ("annualized_clothing_footwear_spend_krw", ("연간", "의류", "신발")),
    ("monthly_clothing_footwear_spend_krw", ("의류", "신발")),
    ("monthly_disposable_income_krw", ("처분가능", "소득")),
    ("monthly_household_income_krw", ("월평균", "소득")),
    ("annual_household_income_krw", ("평균", "소득")),
    ("household_net_assets_krw", ("순자산",)),
    ("household_assets_krw", ("자산",)),
    ("household_debt_krw", ("부채",)),
)


@dataclass(frozen=True)
class KosisMetric:
    segment_id: str
    segment_label: str
    metric: str
    period: str
    value_krw: float
    source_name: str
    source_url: str
    unit: str = "KRW"
    note: str = ""


def price_burden_ratio(product_price_krw: int, denominator_krw: int | None = None) -> float:
    """ratio = product_price / annualized clothing-footwear denominator."""
    if product_price_krw <= 0:
        raise ValueError(f"product_price_krw must be positive, got {product_price_krw}")
    denominator = int(denominator_krw or KOSTAT_2025_ANNUAL_CLOTHING_FOOTWEAR_KRW)
    if denominator <= 0:
        raise ValueError(f"denominator_krw must be positive, got {denominator}")
    return product_price_krw / denominator


def price_burden_label(ratio: float) -> Literal["low", "medium", "high", "very_high"]:
    """Annual clothing-footwear spend 기준 상대 라벨.

    ratio <= 0.05        → low
    0.05 < ratio <= 0.12 → medium
    0.12 < ratio <= 0.25 → high
    ratio > 0.25         → very_high
    """
    import math

    if not isinstance(ratio, int | float) or math.isnan(ratio) or math.isinf(ratio):
        raise ValueError(f"ratio must be finite number, got {ratio!r}")
    if ratio <= 0:
        raise ValueError(f"ratio must be positive, got {ratio}")
    if ratio <= 0.05:
        return "low"
    if ratio <= 0.12:
        return "medium"
    if ratio <= 0.25:
        return "high"
    return "very_high"


def load_kosis_snapshot(path: Path = KOSIS_SNAPSHOT_PATH) -> list[KosisMetric]:
    """Load committed KOSIS/KOSTAT context snapshot."""
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            KosisMetric(
                segment_id=str(row["segment_id"]),
                segment_label=str(row["segment_label"]),
                metric=str(row["metric"]),
                period=str(row["period"]),
                value_krw=float(row["value_krw"]),
                source_name=str(row["source_name"]),
                source_url=str(row["source_url"]),
                unit=str(row.get("unit", "KRW") or "KRW"),
                note=str(row.get("note", "")),
            )
            for row in reader
        ]


def kosis_segment_options(metrics: list[KosisMetric] | None = None) -> dict[str, str]:
    """Return segment_id → segment_label options in snapshot order."""
    metrics = metrics if metrics is not None else load_kosis_snapshot()
    options: dict[str, str] = {}
    for row in metrics:
        options.setdefault(row.segment_id, row.segment_label)
    return options


def _selected_metrics(metrics: list[KosisMetric], segment_id: str) -> tuple[list[KosisMetric], str]:
    options = kosis_segment_options(metrics)
    selected_segment = segment_id if segment_id in options else DEFAULT_REFERENCE_SEGMENT_ID

    national = [row for row in metrics if row.segment_id == DEFAULT_REFERENCE_SEGMENT_ID]
    selected = [row for row in metrics if row.segment_id == selected_segment]

    by_metric: dict[str, KosisMetric] = {row.metric: row for row in national}
    for row in selected:
        by_metric[row.metric] = row

    metric_order = list(REFERENCE_METRIC_LABELS)
    ordered = sorted(
        by_metric.values(),
        key=lambda row: (
            metric_order.index(row.metric)
            if row.metric in REFERENCE_METRIC_LABELS
            else len(metric_order)
        ),
    )
    return ordered, options.get(selected_segment, DEFAULT_REFERENCE_SEGMENT_LABEL)


def _metric_value(rows: list[KosisMetric], metric: str) -> int | None:
    for row in rows:
        if row.metric == metric:
            return row.value_krw
    return None


def _period_summary(rows: list[KosisMetric]) -> str:
    periods = sorted({row.period for row in rows})
    return ", ".join(periods)


def _hash_payload(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _context_digest(rows: list[KosisMetric], segment_id: str, source_mode: str) -> str:
    return _hash_payload(
        {
            "segment_id": segment_id,
            "source_mode": source_mode,
            "rows": [
                {
                    "metric": row.metric,
                    "period": row.period,
                    "value_krw": row.value_krw,
                    "source_name": row.source_name,
                }
                for row in rows
            ],
        }
    )


def _unit_multiplier(unit_name: str) -> int:
    text = unit_name.lower()
    if "억원" in text:
        return 100_000_000
    if "백만원" in text:
        return 1_000_000
    if "만원" in text:
        return 10_000
    if "천원" in text:
        return 1_000
    return 1


def _metric_unit(metric: str, unit_name: str) -> str:
    if metric == "consumer_price_index_clothing_footwear":
        return unit_name.strip() or "index"
    return "KRW"


def _detect_metric_name(row: dict[str, Any]) -> str | None:
    candidates = " ".join(
        str(row.get(key, ""))
        for key in (
            "ITM_NM",
            "ITM_NM_ENG",
            "C1_NM",
            "C2_NM",
            "C3_NM",
            "C4_NM",
            "TBL_NM",
        )
    )
    compact = candidates.replace(" ", "")
    for metric, keywords in _API_METRIC_KEYWORDS:
        if all(keyword.replace(" ", "") in compact for keyword in keywords):
            return metric
    return None


def _api_segment_label(row: dict[str, Any]) -> str:
    labels = [
        str(row[key])
        for key in ("C1_NM", "C2_NM", "C3_NM", "C4_NM")
        if key in row and str(row[key]).strip()
    ]
    return " / ".join(labels) or "KOSIS API 선택값"


def _parse_number(value: Any) -> float | None:
    text = str(value).replace(",", "").strip()
    if not text or text in {"-", "…"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_kosis_api_metrics(rows: list[dict[str, Any]]) -> list[KosisMetric]:
    """Parse generic KOSIS statisticsData JSON rows into known metrics."""
    parsed: list[KosisMetric] = []
    for row in rows:
        metric = _detect_metric_name(row)
        raw_value = _parse_number(row.get("DT"))
        if metric is None or raw_value is None:
            continue
        unit = str(row.get("UNIT_NM", ""))
        normalized_unit = _metric_unit(metric, unit)
        if normalized_unit == "KRW":
            value = int(round(raw_value * _unit_multiplier(unit)))
        else:
            value = raw_value
        segment_label = _api_segment_label(row)
        parsed.append(
            KosisMetric(
                segment_id="api_selected",
                segment_label=segment_label,
                metric=metric,
                period=str(row.get("PRD_DE", "")),
                value_krw=value,
                source_name=str(row.get("TBL_NM", "KOSIS statisticsData API")),
                source_url="https://kosis.kr/openapi/statisticsData.do",
                unit=normalized_unit,
                note="KOSIS API refresh",
            )
        )
    return parsed


def _with_api_key(url: str, api_key: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["apiKey"] = api_key
    query["format"] = "json"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def validate_kosis_statistics_data_url(url: str) -> str:
    """Validate a user-supplied KOSIS statisticsData URL before appending secrets.

    If more KOSIS API paths are supported later, expand KOSIS_STATISTICS_DATA_PATH
    to an explicit allowlist instead of relaxing the host-only check.
    """
    cleaned_url = url.strip()
    parts = urlsplit(cleaned_url)
    hostname = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != "https":
        raise ValueError("KOSIS statisticsData URL must use https.")
    if hostname not in _KOSIS_ALLOWED_HOSTS:
        raise ValueError(f"KOSIS statisticsData URL host is not allowed: {hostname or '<empty>'}")
    if parts.path != KOSIS_STATISTICS_DATA_PATH:
        raise ValueError("KOSIS statisticsData URL path is not allowed.")
    return cleaned_url


def fetch_kosis_api_metrics(
    api_key: str,
    statistics_data_url: str,
    timeout: float = 10.0,
) -> list[KosisMetric]:
    """Fetch user-selected KOSIS statisticsData URL and parse known metrics.

    The API key is appended only for the request. It is never returned.
    """
    if not api_key.strip() or not statistics_data_url.strip():
        return []
    validated_url = validate_kosis_statistics_data_url(statistics_data_url)
    request_url = _with_api_key(validated_url, api_key.strip())
    response = httpx.get(request_url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        if data.get("err"):
            raise ValueError("KOSIS API returned an error response")
        data = [data]
    if not isinstance(data, list):
        raise ValueError("KOSIS API response must be a JSON object or array")
    rows = [row for row in data if isinstance(row, dict)]
    return parse_kosis_api_metrics(rows)


def build_price_context(
    product_price_krw: int,
    *,
    reference_segment_id: str = DEFAULT_REFERENCE_SEGMENT_ID,
    snapshot_path: Path = KOSIS_SNAPSHOT_PATH,
    use_api_refresh: bool = False,
    kosis_api_key: str = "",
    kosis_api_url: str = "",
) -> dict[str, Any]:
    """Build compact context used by UI, prompt, cache hash, and report."""
    snapshot_metrics = load_kosis_snapshot(snapshot_path)
    warnings: list[str] = []
    source_mode = "snapshot"
    api_status = "snapshot"
    all_metrics = list(snapshot_metrics)

    if use_api_refresh:
        if not kosis_api_key.strip() or not kosis_api_url.strip():
            api_status = "missing_api_key"
            warnings.append("KOSIS API 갱신에는 API key와 statisticsData URL이 모두 필요합니다.")
        else:
            try:
                api_metrics = fetch_kosis_api_metrics(kosis_api_key, kosis_api_url)
            except Exception as exc:  # noqa: BLE001 - UI falls back to snapshot with a warning.
                api_status = "failed"
                warnings.append(f"KOSIS API 갱신 실패: {type(exc).__name__}")
            else:
                if api_metrics:
                    api_status = "success"
                    source_mode = "api"
                    all_metrics.extend(api_metrics)
                    reference_segment_id = "api_selected"
                else:
                    api_status = "failed"
                    warnings.append(
                        "KOSIS API 응답에서 지원하는 통계 항목을 찾지 못해 스냅샷을 사용합니다."
                    )

    selected_rows, segment_label = _selected_metrics(all_metrics, reference_segment_id)
    annual_clothing = _metric_value(selected_rows, "annualized_clothing_footwear_spend_krw")
    monthly_clothing = _metric_value(selected_rows, "monthly_clothing_footwear_spend_krw")
    denominator = annual_clothing or (monthly_clothing * 12 if monthly_clothing else None)
    if denominator is None:
        denominator = KOSTAT_2025_ANNUAL_CLOTHING_FOOTWEAR_KRW
        warnings.append("의류·신발 지출 기준값이 없어 기본 기준값을 사용합니다.")

    ratio = price_burden_ratio(product_price_krw, denominator)
    metrics = {row.metric: row.value_krw for row in selected_rows}
    source_names = sorted({row.source_name for row in selected_rows})
    source_urls = sorted({row.source_url for row in selected_rows if row.source_url})
    return {
        "source": "kosis",
        "source_mode": source_mode,
        "api_status": api_status,
        "source_name": "; ".join(source_names),
        "source_urls": source_urls,
        "reference_segment_id": reference_segment_id,
        "reference_segment_label": segment_label,
        "period": _period_summary(selected_rows),
        "denominator_krw": int(denominator),
        "price_burden_ratio": ratio,
        "price_burden_label": price_burden_label(ratio),
        "metrics": metrics,
        "metric_rows": [
            {
                "metric": row.metric,
                "label": REFERENCE_METRIC_LABELS.get(row.metric, row.metric),
                "period": row.period,
                "value": row.value_krw,
                "value_krw": row.value_krw,
                "unit": row.unit,
                "source_name": row.source_name,
                "note": row.note,
            }
            for row in selected_rows
        ],
        "warnings": tuple(warnings),
        "context_digest": _context_digest(selected_rows, reference_segment_id, source_mode),
    }
