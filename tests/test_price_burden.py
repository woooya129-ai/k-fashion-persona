import pytest

from src.economic_context import price_burden_label, price_burden_ratio

pytestmark = pytest.mark.no_network


@pytest.mark.parametrize(
    "price,expected_ratio,expected_label",
    [
        (50_000, pytest.approx(50_000 / 141_000), "low"),
        (70_500, pytest.approx(0.5), "low"),  # 경계 (포함)
        (70_501, pytest.approx(70_501 / 141_000), "medium"),  # 경계 (다음)
        (141_000, pytest.approx(1.0), "medium"),
        (159_000, pytest.approx(159_000 / 141_000), "medium"),  # PM 예시
        (169_200, pytest.approx(1.2), "medium"),  # 경계 (포함)
        (169_201, pytest.approx(169_201 / 141_000), "high"),  # 경계 (다음)
        (200_000, pytest.approx(200_000 / 141_000), "high"),
        (282_000, pytest.approx(2.0), "high"),  # 경계 (포함)
        (282_001, pytest.approx(282_001 / 141_000), "very_high"),  # 경계 (다음)
        (500_000, pytest.approx(500_000 / 141_000), "very_high"),
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
