from __future__ import annotations

import pytest

from src.public_data import DataGoKrAuthAdapter, KosisAuthAdapter, PublicDataCache, SourceMetadata

pytestmark = pytest.mark.no_network


def test_kosis_auth_adapter_applies_api_key_and_json_format() -> None:
    url, params = KosisAuthAdapter("kosis-key").apply("https://kosis.kr/openapi", {"a": "b"})
    assert url == "https://kosis.kr/openapi"
    assert params["a"] == "b"
    assert params["apiKey"] == "kosis-key"
    assert params["format"] == "json"


def test_datagokr_auth_adapter_applies_service_key_and_json_type() -> None:
    _, params = DataGoKrAuthAdapter("service-key").apply(
        "https://apis.data.go.kr/example",
        {},
    )
    assert params["serviceKey"] == "service-key"
    assert params["type"] == "json"


def test_public_data_cache_round_trip_and_clear() -> None:
    cache = PublicDataCache()
    assert cache.get("missing") is None
    assert cache.set("k", {"ok": True}) == {"ok": True}
    assert cache.get("k") == {"ok": True}
    cache.clear()
    assert cache.get("k") is None


def test_source_metadata_status_contract() -> None:
    meta = SourceMetadata(
        name="KOSIS",
        source_url="https://kosis.kr",
        status="snapshot",
        period="2025_Q4",
    )
    assert meta.name == "KOSIS"
    assert meta.status == "snapshot"
