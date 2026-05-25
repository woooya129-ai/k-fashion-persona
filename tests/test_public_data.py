from __future__ import annotations

import pytest

from src.public_data import (
    DataGoKrAuthAdapter,
    KosisAuthAdapter,
    PublicDataCache,
    SourceMetadata,
)
from src.public_data.population import (
    PopulationRow,
    build_population_context,
    fetch_population_api_rows,
    load_population_snapshot,
    parse_population_api_rows,
)

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


def test_population_snapshot_loads_national_row() -> None:
    rows = load_population_snapshot()

    national = next(row for row in rows if row.region_label == "전국")
    assert national.period == "2026-04"
    assert national.total == 51_097_986
    assert national.unit == "persons"


def test_population_context_missing_key_uses_snapshot() -> None:
    context = build_population_context(
        age_min=20,
        age_max=39,
        sex={"F"},
        provinces={"서울"},
        use_api_refresh=True,
        service_key="",
        api_url="",
    )

    assert context["api_status"] == "missing_api_key"
    assert context["source_mode"] == "snapshot"
    assert context["reference_region_label"] == "서울특별시"
    assert context["target_age_population"] == 2_706_940
    assert context["target_age_bucket_basis"] == ("20-29", "30-39")
    assert context["target_age_bucket_basis_label"] == "20-29, 30-39"
    assert "주변분포" in context["population_scope_note"]
    assert context["target_sex_label"] == "F"
    assert context["target_sex_population"] == 4_821_211


def test_population_context_off_bucket_age_range_discloses_bucket_basis() -> None:
    context = build_population_context(
        age_min=25,
        age_max=34,
        sex={"F"},
        provinces={"서울"},
    )

    assert context["target_age_range"] == "25-34"
    assert context["target_age_bucket_basis"] == ("20-29", "30-39")
    assert context["target_age_population"] == 2_706_940
    assert "성별, 연령, 지역을 모두 교차한 값이 아니라" in context["population_scope_note"]


def test_population_context_api_failure_uses_snapshot() -> None:
    def fail_fetch_rows_fn(**_: object) -> list[PopulationRow]:
        raise RuntimeError("boom")

    context = build_population_context(
        age_min=20,
        age_max=39,
        provinces={"서울"},
        use_api_refresh=True,
        service_key="fake-service-key",
        api_url="https://apis.data.go.kr/1741000/mock/getRows",
        fetch_rows_fn=fail_fetch_rows_fn,
    )

    assert context["api_status"] == "failed"
    assert context["source_mode"] == "snapshot"
    assert context["target_age_population"] == 2_706_940
    assert any("API 갱신 실패, 스냅샷 사용" in warning for warning in context["warnings"])


def test_parse_population_api_rows_accepts_common_json_shape() -> None:
    rows = parse_population_api_rows(
        [
            {
                "시도명": "서울특별시",
                "기준년월": "202604",
                "총인구수": "9,298,673",
                "남자인구수": "4,477,462",
                "여자인구수": "4,821,211",
                "age_20-29": "1,239,522",
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0].region_label == "서울특별시"
    assert rows[0].period == "2026-04"
    assert rows[0].age_counts["20-29"] == 1_239_522


def test_parse_population_api_rows_accepts_korean_sex_age_fields() -> None:
    rows = parse_population_api_rows(
        [
            {
                "시도명": "서울특별시",
                "기준년월": "202604",
                "총인구수": "9,298,673",
                "남자인구수": "4,477,462",
                "여자인구수": "4,821,211",
                "만20~29세남자": "600,000",
                "만20~29세여자": "639,522",
            }
        ]
    )

    assert rows[0].age_counts["20-29"] == 1_239_522


def test_parse_population_api_rows_aggregates_subregion_rows_to_province() -> None:
    rows = parse_population_api_rows(
        [
            {
                "시도명": "서울특별시",
                "시군구명": "종로구",
                "행정동명": "청운효자동",
                "기준년월": "202604",
                "총인구수": "100",
                "남자인구수": "45",
                "여자인구수": "55",
                "만20~29세남자": "10",
                "만20~29세여자": "15",
            },
            {
                "시도명": "서울특별시",
                "시군구명": "중구",
                "행정동명": "소공동",
                "기준년월": "202604",
                "총인구수": "200",
                "남자인구수": "95",
                "여자인구수": "105",
                "만20~29세남자": "20",
                "만20~29세여자": "25",
            },
        ]
    )

    assert len(rows) == 1
    assert rows[0].region_label == "서울특별시"
    assert rows[0].total == 300
    assert rows[0].male == 140
    assert rows[0].female == 160
    assert rows[0].age_counts["20-29"] == 70


def test_fetch_population_api_rows_rejects_unapproved_path(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_get(*_: object, **__: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("httpx.get should not be called")

    monkeypatch.setattr("src.public_data.population.connector.httpx.get", fake_get)

    with pytest.raises(ValueError, match="path"):
        fetch_population_api_rows(
            service_key="fake-service-key",
            api_url="https://apis.data.go.kr/not-mois/mock",
        )

    assert called is False


def test_fetch_population_api_rows_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, str]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "response": {
                    "body": {
                        "items": {
                            "item": [
                                {
                                    "시도명": "서울특별시",
                                    "기준년월": "202604",
                                    "총인구수": "9,298,673",
                                    "남자인구수": "4,477,462",
                                    "여자인구수": "4,821,211",
                                }
                            ]
                        }
                    }
                }
            }

    def fake_get(_url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        assert timeout == 10.0
        calls.append(params)
        return FakeResponse()

    monkeypatch.setattr("src.public_data.population.connector.httpx.get", fake_get)
    cache = PublicDataCache()
    api_url = "https://apis.data.go.kr/1741000/mock/getRows"

    first = fetch_population_api_rows(
        service_key="fake-service-key",
        api_url=api_url,
        cache=cache,
    )
    second = fetch_population_api_rows(
        service_key="fake-service-key",
        api_url=api_url,
        cache=cache,
    )

    assert len(first) == 1
    assert second == first
    assert len(calls) == 1
    assert calls[0]["serviceKey"] == "fake-service-key"
    assert calls[0]["type"] == "json"
