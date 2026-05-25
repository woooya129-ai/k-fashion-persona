# SPDX-License-Identifier: AGPL-3.0-only
"""SBDC commercial-area context connector.

The output is report-only aggregate context. It must not change persona
sampling, prompt cache keys, or model scores.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import urlsplit

import httpx

from src.public_data import DataGoKrAuthAdapter, PublicDataCache

SBDC_COMMERCIAL_DATA_URL = "https://www.data.go.kr/data/15012005/openapi.do"
SBDC_COMMERCIAL_API_URL_VAR = "SBDC_COMMERCIAL_API_URL"

_ALLOWED_API_HOSTS = frozenset({"apis.data.go.kr"})
_ALLOWED_API_PATH_PREFIXES = ("/B553077/api/open/sdsc2/",)
_SOURCE_NAME = "소상공인시장진흥공단 상가(상권)정보 API"
_CONTEXT_NOTE = "상가(상권)정보는 업종 집계 참고값이며 개인 수요, 판매량, 매출을 추정하지 않습니다."
_COMMERCIAL_KEYWORDS = (
    "패션",
    "의류",
    "옷",
    "잡화",
    "신발",
    "가방",
    "소매",
    "편집숍",
    "부티크",
)
_OFFLINE_KEYWORDS = ("오프라인", "매장", "상권", "팝업", "리테일", "백화점", "편집숍")
_REGION_KEYS = ("ctprvnNm", "시도명", "signguNm", "시군구명", "adongNm", "행정동명")
_INDUSTRY_KEYS = ("indsSclsNm", "indsMclsNm", "indsLclsNm", "상권업종소분류명", "상권업종중분류명")
_PERIOD_KEYS = ("stdrYm", "기준년월", "modifiedAt", "lastModified")


def _hash_payload(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_api_url(api_url: str) -> str:
    cleaned = api_url.strip()
    parts = urlsplit(cleaned)
    hostname = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != "https":
        raise ValueError("SBDC commercial API URL must use https.")
    if hostname not in _ALLOWED_API_HOSTS:
        raise ValueError(f"SBDC commercial API URL host is not allowed: {hostname or '<empty>'}")
    if not any(parts.path.startswith(prefix) for prefix in _ALLOWED_API_PATH_PREFIXES):
        raise ValueError("SBDC commercial API URL path is not allowed.")
    return cleaned


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


def _first_region(provinces: Iterable[str]) -> str:
    for province in provinces:
        label = str(province).strip()
        if label and label != "전국":
            return label
    return ""


def _concept_text(concept: dict[str, Any] | None) -> str:
    if not concept:
        return ""
    keys = (
        "category",
        "occasion",
        "target_hypothesis",
        "description",
        "concept_text",
        "canonical_product_card_text",
    )
    return " ".join(str(concept.get(key) or "") for key in keys)


def _needs_offline_context(concept: dict[str, Any] | None) -> bool:
    text = _concept_text(concept)
    return any(keyword in text for keyword in _OFFLINE_KEYWORDS)


def _industry_keywords(concept: dict[str, Any] | None) -> tuple[str, ...]:
    text = _concept_text(concept)
    found = tuple(keyword for keyword in _COMMERCIAL_KEYWORDS if keyword in text)
    return found


def _region_params(region_label: str) -> dict[str, str]:
    if not region_label:
        return {}
    return {"ctprvnNm": region_label}


def fetch_commercial_rows(
    *,
    service_key: str,
    api_url: str,
    params: dict[str, str] | None = None,
    cache: PublicDataCache | None = None,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    """Fetch raw SBDC commercial rows from a reviewed data.go.kr endpoint."""
    if not service_key.strip() or not api_url.strip():
        return []
    url = _validate_api_url(api_url)
    request_params = {"pageNo": "1", "numOfRows": "1000"}
    if params:
        request_params.update(params)
    cache_key = _hash_payload({"source": "sbdc_commercial", "url": url, "params": request_params})
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached
    url, request_params = DataGoKrAuthAdapter(service_key).apply(url, request_params)
    response = httpx.get(url, params=request_params, timeout=timeout)
    response.raise_for_status()
    rows = _extract_items(response.json())
    if cache is not None:
        cache.set(cache_key, rows)
    return rows


def _row_text(row: dict[str, Any], keys: Iterable[str]) -> str:
    return " ".join(str(row.get(key) or "") for key in keys).strip()


def _period(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        for key in _PERIOD_KEYS:
            value = str(row.get(key) or "").strip()
            if value:
                return f"{value[:4]}-{value[4:]}" if len(value) == 6 and value.isdigit() else value
    return ""


def _metric_rows(
    rows: list[dict[str, Any]],
    *,
    industry_keywords: tuple[str, ...],
    period: str,
) -> list[dict[str, Any]]:
    matched = []
    for row in rows:
        industry_text = _row_text(row, _INDUSTRY_KEYS)
        if any(keyword in industry_text for keyword in industry_keywords):
            matched.append(row)
    if not matched:
        return []

    industry_counts = Counter(_row_text(row, _INDUSTRY_KEYS) or "미분류" for row in matched)
    metrics: list[dict[str, Any]] = [
        {
            "label": "상가정보 관련 업종 수",
            "value": len(matched),
            "unit": "count",
            "period": period,
            "source_name": _SOURCE_NAME,
            "source_url": SBDC_COMMERCIAL_DATA_URL,
            "note": "상호, 주소, 좌표 원천 항목은 리포트에 저장하지 않습니다.",
        }
    ]
    for label, count in industry_counts.most_common(5):
        metrics.append(
            {
                "label": f"상가정보 업종 분포: {label}",
                "value": count,
                "unit": "count",
                "period": period,
                "source_name": _SOURCE_NAME,
                "source_url": SBDC_COMMERCIAL_DATA_URL,
            }
        )
    return metrics


def build_commercial_context(
    *,
    concept: dict[str, Any] | None = None,
    provinces: Iterable[str] = (),
    use_api_refresh: bool = False,
    service_key: str = "",
    api_url: str = "",
    cache: PublicDataCache | None = None,
    fetch_rows_fn: Callable[..., list[dict[str, Any]]] = fetch_commercial_rows,
) -> dict[str, Any]:
    warnings: list[str] = []
    region_label = _first_region(provinces)
    base = {
        "source": "sbdc_commercial",
        "title": "상가(상권)정보 참고",
        "provider": "소상공인시장진흥공단 / data.go.kr",
        "source_name": _SOURCE_NAME,
        "source_url": SBDC_COMMERCIAL_DATA_URL,
        "reference_region_label": region_label or "전국",
        "period": "",
        "api_status": "not_used",
        "metric_rows": [],
        "context_note": _CONTEXT_NOTE,
        "warnings": tuple(warnings),
    }
    if not region_label:
        return base | {"warnings": ("지역 입력이 없어 상가(상권)정보를 사용하지 않았습니다.",)}
    if not _needs_offline_context(concept):
        return base | {
            "warnings": ("오프라인 판매/상권 맥락이 없어 상가정보를 사용하지 않았습니다.",)
        }
    industry_keywords = _industry_keywords(concept)
    if not industry_keywords:
        return base | {"warnings": ("상가정보 업종 필터 키워드가 없어 사용하지 않았습니다.",)}
    if not use_api_refresh:
        return base | {"warnings": ("상가정보 API 갱신을 사용하지 않았습니다.",)}
    if not service_key.strip() or not api_url.strip():
        return base | {
            "api_status": "not_used",
            "warnings": (
                "data.go.kr serviceKey 또는 상가정보 endpoint가 없어 사용하지 않았습니다.",
            ),
        }
    try:
        rows = fetch_rows_fn(
            service_key=service_key,
            api_url=api_url,
            params=_region_params(region_label),
            cache=cache,
        )
    except Exception as exc:  # noqa: BLE001 - optional report context must not block runs.
        return base | {
            "api_status": "failed",
            "warnings": (f"상가정보 API 갱신 실패: {type(exc).__name__}",),
        }
    period = _period(rows)
    metrics = _metric_rows(rows, industry_keywords=industry_keywords, period=period)
    if not metrics:
        return base | {
            "api_status": "failed",
            "warnings": ("상가정보 API 응답에서 관련 업종 집계를 찾지 못했습니다.",),
        }
    digest_rows = [
        {"industry": _row_text(row, _INDUSTRY_KEYS), "region": _row_text(row, _REGION_KEYS)}
        for row in rows[:1000]
    ]
    return base | {
        "api_status": "success",
        "period": period,
        "metric_rows": tuple(metrics),
        "warnings": tuple(warnings),
        "context_digest": _hash_payload(
            {
                "source": "sbdc_commercial",
                "region": region_label,
                "industry_keywords": industry_keywords,
                "rows": digest_rows,
            }
        ),
    }
