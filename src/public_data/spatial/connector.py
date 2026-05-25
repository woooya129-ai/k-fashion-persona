# SPDX-License-Identifier: AGPL-3.0-only
"""SGIS S-Open API context connector.

The output is report-only aggregate context. It must not change persona
sampling, prompt cache keys, or model scores.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import urlsplit

import httpx

from src.public_data import PublicDataCache, SgisAccessTokenAuthAdapter

SGIS_SOURCE_URL = "https://sgis.mods.go.kr/contents/shortcut/shortcut_06.jsp"
SGIS_DEVELOPER_URL = "https://sgis.mods.go.kr/developer"
SGIS_TOKEN_URL = "https://sgisapi.mods.go.kr/OpenAPI3/auth/authentication.json"
SGIS_STARTUP_CORP_COUNT_URL = "https://sgisapi.mods.go.kr/OpenAPI3/startupbiz/sggtobcorpcount.json"
SGIS_SPATIAL_API_URL_VAR = "SGIS_SPATIAL_API_URL"

_ALLOWED_HOSTS = frozenset({"sgisapi.mods.go.kr", "sgisapi.kostat.go.kr"})
_ALLOWED_PATHS = frozenset(
    {
        "/OpenAPI3/auth/authentication.json",
        "/OpenAPI3/stats/population.json",
        "/OpenAPI3/stats/searchpopulation.json",
        "/OpenAPI3/stats/household.json",
        "/OpenAPI3/startupbiz/sidotobinfo.json",
        "/OpenAPI3/startupbiz/sidotobgroup.json",
        "/OpenAPI3/startupbiz/sggtobcorpcount.json",
    }
)
_PROVINCE_CODES: dict[str, str] = {
    "서울": "11",
    "서울특별시": "11",
    "부산": "21",
    "부산광역시": "21",
    "대구": "22",
    "대구광역시": "22",
    "인천": "23",
    "인천광역시": "23",
    "광주": "24",
    "광주광역시": "24",
    "대전": "25",
    "대전광역시": "25",
    "울산": "26",
    "울산광역시": "26",
    "세종": "29",
    "세종특별자치시": "29",
    "경기": "31",
    "경기도": "31",
    "강원": "32",
    "강원특별자치도": "32",
    "충북": "33",
    "충청북도": "33",
    "충남": "34",
    "충청남도": "34",
    "전북": "35",
    "전북특별자치도": "35",
    "전남": "36",
    "전라남도": "36",
    "경북": "37",
    "경상북도": "37",
    "경남": "38",
    "경상남도": "38",
    "제주": "39",
    "제주특별자치도": "39",
}


def _hash_payload(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_number(value: Any) -> float:
    text = str(value or "").replace(",", "").strip()
    if not text or text in {"-", "N/A", "null", "None"}:
        return 0.0
    return float(text)


def _validate_api_url(api_url: str) -> str:
    cleaned = api_url.strip()
    parts = urlsplit(cleaned)
    hostname = (parts.hostname or "").rstrip(".").lower()
    if parts.scheme != "https":
        raise ValueError("SGIS API URL must use https.")
    if hostname not in _ALLOWED_HOSTS:
        raise ValueError(f"SGIS API URL host is not allowed: {hostname or '<empty>'}")
    if parts.path not in _ALLOWED_PATHS:
        raise ValueError("SGIS API URL path is not allowed.")
    return cleaned


def _extract_result(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    err_cd = str(data.get("errCd", "0"))
    if err_cd not in {"0", "None", ""}:
        raise ValueError("SGIS API returned an error response")
    result = data.get("result")
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]
    if isinstance(result, dict):
        rows = result.get("data") or result.get("rows") or result.get("list")
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, dict)]
        return [result]
    return []


def _first_region(provinces: Iterable[str]) -> tuple[str, str]:
    for province in provinces:
        label = str(province).strip()
        if label in _PROVINCE_CODES:
            return label, _PROVINCE_CODES[label]
    return "", ""


def fetch_sgis_access_token(
    *,
    consumer_key: str,
    consumer_secret: str,
    token_url: str = SGIS_TOKEN_URL,
    timeout: float = 10.0,
) -> str:
    if not consumer_key.strip() or not consumer_secret.strip():
        return ""
    url = _validate_api_url(token_url)
    response = httpx.get(
        url,
        params={"consumer_key": consumer_key, "consumer_secret": consumer_secret},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("SGIS token response must be a JSON object")
    if str(data.get("errCd", "0")) not in {"0", "None", ""}:
        raise ValueError("SGIS token request failed")
    result = data.get("result")
    if isinstance(result, dict):
        token = str(result.get("accessToken") or result.get("access_token") or "").strip()
    else:
        token = str(data.get("accessToken") or data.get("access_token") or "").strip()
    if not token:
        raise ValueError("SGIS token response did not include accessToken")
    return token


def fetch_sgis_spatial_rows(
    *,
    access_token: str,
    api_url: str = SGIS_STARTUP_CORP_COUNT_URL,
    params: dict[str, str] | None = None,
    cache: PublicDataCache | None = None,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    if not access_token.strip() or not api_url.strip():
        return []
    url = _validate_api_url(api_url)
    request_params = {"low_search": "0"}
    if params:
        request_params.update(params)
    cache_key = _hash_payload({"source": "sgis_spatial", "url": url, "params": request_params})
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached
    url, request_params = SgisAccessTokenAuthAdapter(access_token).apply(url, request_params)
    response = httpx.get(url, params=request_params, timeout=timeout)
    response.raise_for_status()
    rows = _extract_result(response.json())
    if cache is not None:
        cache.set(cache_key, rows)
    return rows


def _metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    totals = {"population": 0.0, "households": 0.0, "corp_count": 0.0}
    for row in rows:
        totals["population"] += _parse_number(
            row.get("tot_ppltn") or row.get("population") or row.get("ppltn")
        )
        totals["households"] += _parse_number(
            row.get("tot_family") or row.get("household") or row.get("family")
        )
        totals["corp_count"] += _parse_number(row.get("corp_cnt") or row.get("corp_count"))
    metrics = []
    if totals["population"]:
        metrics.append(
            {"label": "SGIS 지역 인구", "value": int(totals["population"]), "unit": "persons"}
        )
    if totals["households"]:
        metrics.append(
            {"label": "SGIS 지역 가구", "value": int(totals["households"]), "unit": "households"}
        )
    if totals["corp_count"]:
        metrics.append(
            {"label": "SGIS 생활업종 사업체", "value": int(totals["corp_count"]), "unit": "count"}
        )
    return metrics


def build_spatial_context(
    *,
    provinces: Iterable[str] = (),
    use_api_refresh: bool = False,
    consumer_key: str = "",
    consumer_secret: str = "",
    token_url: str = SGIS_TOKEN_URL,
    api_url: str = SGIS_STARTUP_CORP_COUNT_URL,
    cache: PublicDataCache | None = None,
    fetch_token_fn: Callable[..., str] = fetch_sgis_access_token,
    fetch_rows_fn: Callable[..., list[dict[str, Any]]] = fetch_sgis_spatial_rows,
) -> dict[str, Any]:
    warnings: list[str] = []
    region_label, adm_cd = _first_region(provinces)
    base = {
        "source": "sgis_spatial",
        "title": "SGIS 공간 통계 참고",
        "provider": "SGIS / KOSTAT",
        "source_name": "SGIS S-Open API",
        "source_url": SGIS_SOURCE_URL,
        "reference_region_label": region_label or "전국",
        "period": "",
        "api_status": "not_used",
        "metric_rows": [],
        "context_note": (
            "SGIS 공간 통계는 집계 참고값이며 페르소나 점수나 표본을 보정하지 않습니다."
        ),
        "warnings": tuple(warnings),
    }
    if not region_label or not adm_cd:
        return base | {"warnings": ("지역 입력이 없어 SGIS 공간 통계를 사용하지 않았습니다.",)}
    if not use_api_refresh:
        return base | {"warnings": ("SGIS API 갱신을 사용하지 않았습니다.",)}
    if not api_url.strip():
        return base | {"warnings": ("SGIS API endpoint가 없어 공간 통계를 사용하지 않았습니다.",)}
    if not consumer_key.strip() or not consumer_secret.strip():
        return base | {
            "api_status": "missing_api_key",
            "warnings": ("SGIS consumer key/secret이 없어 공간 통계를 사용하지 않았습니다.",),
        }
    try:
        access_token = fetch_token_fn(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            token_url=token_url,
        )
        rows = fetch_rows_fn(
            access_token=access_token,
            api_url=api_url,
            params={"adm_cd": adm_cd},
            cache=cache,
        )
    except Exception as exc:  # noqa: BLE001 - optional report context must not block runs.
        return base | {
            "api_status": "failed",
            "warnings": (f"SGIS API 갱신 실패: {type(exc).__name__}",),
        }
    metrics = _metric_rows(rows)
    if not metrics:
        return base | {
            "api_status": "failed",
            "warnings": ("SGIS API 응답에서 지원하는 통계 항목을 찾지 못했습니다.",),
        }
    period = str(rows[0].get("base_year") or rows[0].get("year") or "")
    return base | {
        "api_status": "success",
        "period": period,
        "metric_rows": tuple(
            row
            | {"period": period, "source_name": "SGIS S-Open API", "source_url": SGIS_SOURCE_URL}
            for row in metrics
        ),
        "context_digest": _hash_payload(
            {"source": "sgis_spatial", "region": region_label, "rows": rows}
        ),
    }
