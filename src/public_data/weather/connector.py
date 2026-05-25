# SPDX-License-Identifier: AGPL-3.0-only
"""KMA weather context connector.

The output is report-only aggregate context. It must not change persona
sampling, prompt cache keys, or model scores.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

import httpx

from src.public_data import KmaApiHubAuthAdapter, PublicDataCache

KMA_WEATHER_DATA_URL = "https://apihub.kma.go.kr/apiList.do?seqApi=10"
KMA_WEATHER_API_URL_VAR = "KMA_WEATHER_API_URL"
KMA_FORECAST_NX_VAR = "KMA_FORECAST_NX"
KMA_FORECAST_NY_VAR = "KMA_FORECAST_NY"

_SOURCE_NAME = "기상청 API허브 단기예보"
_ALLOWED_API_HOSTS = frozenset({"apihub.kma.go.kr"})
_ALLOWED_API_PATHS = frozenset(
    {
        "/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst",
        "/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst",
        "/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst",
    }
)
_WEATHER_SENSITIVE_KEYWORDS = (
    "아우터",
    "패딩",
    "코트",
    "자켓",
    "재킷",
    "니트",
    "울",
    "린넨",
    "방수",
    "레인",
    "우비",
    "장마",
    "한파",
    "폭염",
    "겨울",
    "여름",
    "비",
    "눈",
    "부츠",
    "샌들",
)
_CATEGORY_LABELS = {
    "TMP": ("기온", "celsius"),
    "TMN": ("최저기온", "celsius"),
    "TMX": ("최고기온", "celsius"),
    "POP": ("강수확률", "percent"),
    "PCP": ("강수량", "mm"),
    "SKY": ("하늘상태", "code"),
    "PTY": ("강수형태", "code"),
    "WSD": ("풍속", "mps"),
}
_CONTEXT_NOTE = "기상 정보는 시점성 참고값이며 페르소나 반응 점수나 표본을 보정하지 않습니다."


def _hash_payload(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_api_url(api_url: str) -> str:
    cleaned = api_url.strip()
    parts = urlsplit(cleaned)
    hostname = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != "https":
        raise ValueError("KMA weather API URL must use https.")
    if hostname not in _ALLOWED_API_HOSTS:
        raise ValueError(f"KMA weather API URL host is not allowed: {hostname or '<empty>'}")
    if parts.path not in _ALLOWED_API_PATHS:
        raise ValueError("KMA weather API URL path is not allowed.")
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


def _concept_text(concept: dict[str, Any] | None) -> str:
    if not concept:
        return ""
    keys = (
        "category",
        "material",
        "season",
        "occasion",
        "target_hypothesis",
        "description",
        "concept_text",
        "canonical_product_card_text",
    )
    return " ".join(str(concept.get(key) or "") for key in keys)


def _is_weather_sensitive(concept: dict[str, Any] | None) -> bool:
    text = _concept_text(concept)
    return any(keyword in text for keyword in _WEATHER_SENSITIVE_KEYWORDS)


def _default_forecast_params(nx: int, ny: int) -> dict[str, str]:
    # KMA short-term endpoints need a base date/time. This default is a stable,
    # conservative request shape; deployments can override via explicit params.
    now = datetime.now(UTC)
    return {
        "pageNo": "1",
        "numOfRows": "1000",
        "dataType": "JSON",
        "base_date": now.strftime("%Y%m%d"),
        "base_time": "0500",
        "nx": str(nx),
        "ny": str(ny),
    }


def fetch_weather_rows(
    *,
    auth_key: str,
    api_url: str,
    nx: int,
    ny: int,
    params: dict[str, str] | None = None,
    cache: PublicDataCache | None = None,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    """Fetch raw KMA weather rows from a reviewed APIHub endpoint."""
    if not auth_key.strip() or not api_url.strip():
        return []
    url = _validate_api_url(api_url)
    request_params = _default_forecast_params(nx, ny)
    if params:
        request_params.update(params)
    cache_key = _hash_payload({"source": "kma_weather", "url": url, "params": request_params})
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached
    url, request_params = KmaApiHubAuthAdapter(auth_key).apply(url, request_params)
    response = httpx.get(url, params=request_params, timeout=timeout)
    response.raise_for_status()
    rows = _extract_items(response.json())
    if cache is not None:
        cache.set(cache_key, rows)
    return rows


def _metric_value(row: dict[str, Any]) -> Any:
    return row.get("fcstValue", row.get("obsrValue", row.get("value", "")))


def _metric_period(row: dict[str, Any]) -> str:
    date = str(row.get("fcstDate") or row.get("baseDate") or row.get("date") or "").strip()
    time = str(row.get("fcstTime") or row.get("baseTime") or row.get("time") or "").strip()
    if date and time:
        return f"{date} {time}"
    return date or time


def _metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        category = str(row.get("category") or "").strip().upper()
        if category not in _CATEGORY_LABELS or category in seen:
            continue
        label, unit = _CATEGORY_LABELS[category]
        metrics.append(
            {
                "label": f"KMA {label}",
                "value": _metric_value(row),
                "unit": unit,
                "period": _metric_period(row),
                "source_name": _SOURCE_NAME,
                "source_url": KMA_WEATHER_DATA_URL,
            }
        )
        seen.add(category)
    return metrics


def build_weather_context(
    *,
    concept: dict[str, Any] | None = None,
    nx: int | None = None,
    ny: int | None = None,
    use_api_refresh: bool = False,
    auth_key: str = "",
    api_url: str = "",
    cache: PublicDataCache | None = None,
    fetch_rows_fn: Callable[..., list[dict[str, Any]]] = fetch_weather_rows,
) -> dict[str, Any]:
    base = {
        "source": "kma_weather",
        "title": "기상청 날씨/시즌 참고",
        "provider": "기상청 API허브",
        "source_name": _SOURCE_NAME,
        "source_url": KMA_WEATHER_DATA_URL,
        "reference_region_label": f"격자 {nx},{ny}" if nx is not None and ny is not None else "",
        "period": "",
        "api_status": "not_used",
        "metric_rows": [],
        "context_note": _CONTEXT_NOTE,
        "warnings": (),
    }
    if not _is_weather_sensitive(concept):
        return base | {"warnings": ("날씨 민감 카테고리나 시즌 맥락이 없어 사용하지 않았습니다.",)}
    if nx is None or ny is None:
        return base | {"warnings": ("기상청 격자 좌표가 없어 날씨 참고값을 사용하지 않았습니다.",)}
    if not use_api_refresh:
        return base | {"warnings": ("기상청 API 갱신을 사용하지 않았습니다.",)}
    if not auth_key.strip() or not api_url.strip():
        return base | {
            "api_status": "missing_api_key",
            "warnings": ("KMA authKey 또는 endpoint가 없어 날씨 참고값을 사용하지 않았습니다.",),
        }
    try:
        rows = fetch_rows_fn(auth_key=auth_key, api_url=api_url, nx=nx, ny=ny, cache=cache)
    except Exception as exc:  # noqa: BLE001 - optional report context must not block runs.
        return base | {
            "api_status": "failed",
            "warnings": (f"기상청 API 갱신 실패: {type(exc).__name__}",),
        }
    metrics = _metric_rows(rows)
    if not metrics:
        return base | {
            "api_status": "failed",
            "warnings": ("기상청 API 응답에서 지원하는 예보 항목을 찾지 못했습니다.",),
        }
    period = str(metrics[0].get("period") or "")
    return base | {
        "api_status": "success",
        "period": period,
        "metric_rows": tuple(metrics),
        "context_digest": _hash_payload(
            {"source": "kma_weather", "nx": nx, "ny": ny, "rows": rows[:1000]}
        ),
    }
