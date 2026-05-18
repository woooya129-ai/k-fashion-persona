import pytest

from src.economic_context import (
    build_price_context,
    fetch_kosis_api_metrics,
    kosis_segment_options,
    parse_kosis_api_metrics,
    price_burden_label,
    price_burden_ratio,
    validate_kosis_statistics_data_url,
)

pytestmark = pytest.mark.no_network


@pytest.mark.parametrize(
    "price,expected_ratio,expected_label",
    [
        (50_000, pytest.approx(50_000 / 2_136_000), "low"),
        (106_800, pytest.approx(0.05), "low"),  # 경계 (포함)
        (106_801, pytest.approx(106_801 / 2_136_000), "medium"),  # 경계 (다음)
        (159_000, pytest.approx(159_000 / 2_136_000), "medium"),  # 대표 입력값
        (256_320, pytest.approx(0.12), "medium"),  # 경계 (포함)
        (256_321, pytest.approx(256_321 / 2_136_000), "high"),  # 경계 (다음)
        (500_000, pytest.approx(500_000 / 2_136_000), "high"),
        (534_000, pytest.approx(0.25), "high"),  # 경계 (포함)
        (534_001, pytest.approx(534_001 / 2_136_000), "very_high"),  # 경계 (다음)
        (800_000, pytest.approx(800_000 / 2_136_000), "very_high"),
    ],
)
def test_price_burden(price, expected_ratio, expected_label):
    ratio = price_burden_ratio(price)
    assert ratio == expected_ratio
    assert price_burden_label(ratio) == expected_label


def test_price_burden_zero_raises():
    with pytest.raises(ValueError):
        price_burden_ratio(0)


def test_price_burden_negative_raises():
    with pytest.raises(ValueError):
        price_burden_ratio(-1)


# M1 해소 (current-update-review 2026-05-01): price_burden_label 단독 호출 보호.
def test_price_burden_label_zero_raises():
    with pytest.raises(ValueError):
        price_burden_label(0.0)


def test_price_burden_label_negative_raises():
    with pytest.raises(ValueError):
        price_burden_label(-0.1)


def test_price_burden_label_nan_raises():
    import math

    with pytest.raises(ValueError):
        price_burden_label(math.nan)


def test_price_burden_label_inf_raises():
    import math

    with pytest.raises(ValueError):
        price_burden_label(math.inf)


def test_kosis_snapshot_context_includes_income_and_asset_metrics():
    context = build_price_context(159_000)

    assert context["source"] == "kosis"
    assert context["source_mode"] == "snapshot"
    assert context["api_status"] == "snapshot"
    assert context["denominator_krw"] == 2_136_000
    assert context["price_burden_ratio"] == pytest.approx(159_000 / 2_136_000)
    assert context["price_burden_label"] == "medium"
    assert context["metrics"]["monthly_household_income_krw"] == 5_422_000
    assert context["metrics"]["household_assets_krw"] == 566_780_000
    assert context["source_urls"]
    assert context["context_digest"]


def test_kosis_reference_segment_overlays_selected_income_metrics():
    context = build_price_context(159_000, reference_segment_id="income_q1")

    assert context["reference_segment_label"] == "소득 1분위"
    assert context["metrics"]["monthly_household_income_krw"] == 1_269_000
    assert context["metrics"]["annualized_clothing_footwear_spend_krw"] == 2_136_000


def test_kosis_segment_options_exposes_committed_segments():
    options = kosis_segment_options()

    assert options["national_all"] == "전국 전체"
    assert options["income_q1"] == "소득 1분위"
    assert options["income_q5"] == "소득 5분위"


def test_kosis_api_refresh_without_key_or_url_falls_back_to_snapshot():
    context = build_price_context(159_000, use_api_refresh=True)

    assert context["source_mode"] == "snapshot"
    assert context["api_status"] == "missing_api_key"
    assert context["warnings"] == (
        "KOSIS API 갱신에는 API key와 statisticsData URL이 모두 필요합니다.",
    )


def test_parse_kosis_api_metrics_converts_unit_to_krw():
    parsed = parse_kosis_api_metrics(
        [
            {
                "TBL_NM": "가계동향조사",
                "C1_NM": "월평균 가구소득",
                "DT": "123.4",
                "UNIT_NM": "만원",
                "PRD_DE": "2025_Q4",
            }
        ]
    )

    assert len(parsed) == 1
    assert parsed[0].metric == "monthly_household_income_krw"
    assert parsed[0].value_krw == 1_234_000
    assert parsed[0].period == "2025_Q4"


def test_validate_kosis_statistics_data_url_accepts_official_url():
    url = "https://kosis.kr/openapi/statisticsData.do?method=getList"

    assert validate_kosis_statistics_data_url(url) == url


@pytest.mark.parametrize(
    "url,match",
    [
        ("http://kosis.kr/openapi/statisticsData.do", "https"),
        ("https://example.com/openapi/statisticsData.do", "host"),
        ("https://kosis.kr.evil.test/openapi/statisticsData.do", "host"),
        ("https://kosis.kr/other/path", "path"),
    ],
)
def test_validate_kosis_statistics_data_url_rejects_unsafe_urls(url, match):
    with pytest.raises(ValueError, match=match):
        validate_kosis_statistics_data_url(url)


def test_fetch_kosis_api_metrics_validates_url_before_appending_api_key(monkeypatch):
    called = False

    def fake_get(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("httpx.get should not be called for invalid KOSIS URL")

    monkeypatch.setattr("src.economic_context.httpx.get", fake_get)

    with pytest.raises(ValueError, match="host"):
        fetch_kosis_api_metrics(
            "fake-kosis-api-key",
            "https://example.com/openapi/statisticsData.do",
        )

    assert called is False
