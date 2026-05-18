"""src/persona_filter.py 테스트."""

import pytest

from src.persona_filter import (
    PersonaFilter,
    SampleResult,
    apply_filter,
    filter_summary,
    preview_first_n,
    sample_iterable_to_result,
    sample_personas,
    sample_to_result,
    sample_with_age_assist,
    take_matching_iterable_to_result,
)
from src.persona_normalizer import Persona

pytestmark = pytest.mark.no_network


def _make(
    persona_id: str, age: int, sex: str, province: str = "서울특별시", occupation: str = "마케터"
) -> Persona:
    return Persona(
        persona_id=persona_id,
        age=age,
        sex=sex,
        province=province,
        district="",
        occupation=occupation,
        marital_status="",
        family_type="",
        housing_type="",
        education_level="",
        persona_summary="test",
        professional_text="",
        lifestyle_text="",
        interests_text="",
        source_row_id=0,
    )


SAMPLE_PERSONAS = [
    _make("p1", 25, "F", "서울특별시", "마케터"),
    _make("p2", 33, "F", "대구광역시", "교사"),
    _make("p3", 42, "M", "부산광역시", "건축가"),
    _make("p4", 19, "M", "서울특별시", "학생"),
    _make("p5", 65, "F", "전라남도", "은퇴"),
]


class TestPersonaFilter:
    def test_no_filter_matches_all(self):
        f = PersonaFilter()
        assert all(f.matches(p) for p in SAMPLE_PERSONAS)

    def test_age_min(self):
        f = PersonaFilter(age_min=30)
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p2", "p3", "p5"}

    def test_age_max(self):
        f = PersonaFilter(age_max=40)
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p1", "p2", "p4"}

    def test_age_range(self):
        f = PersonaFilter(age_min=20, age_max=50)
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p1", "p2", "p3"}

    def test_sex_filter(self):
        f = PersonaFilter(sex=frozenset(["F"]))
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p1", "p2", "p5"}

    def test_province_filter(self):
        f = PersonaFilter(province=frozenset(["서울특별시"]))
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p1", "p4"}

    def test_occupation_contains(self):
        f = PersonaFilter(occupation_contains=frozenset(["교사", "건축"]))
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p2", "p3"}

    def test_combined_filters(self):
        f = PersonaFilter(
            age_min=30,
            age_max=50,
            sex=frozenset(["M"]),
            province=frozenset(["부산광역시"]),
        )
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert {p.persona_id for p in result} == {"p3"}

    def test_zero_match(self):
        f = PersonaFilter(age_min=100)
        result = apply_filter(SAMPLE_PERSONAS, f)
        assert result == []


class TestSamplePersonas:
    def test_deterministic_with_seed(self):
        a = sample_personas(SAMPLE_PERSONAS, 3, seed=42)
        b = sample_personas(SAMPLE_PERSONAS, 3, seed=42)
        assert [p.persona_id for p in a] == [p.persona_id for p in b]

    def test_different_seeds_different_results(self):
        a = sample_personas(SAMPLE_PERSONAS, 3, seed=42)
        b = sample_personas(SAMPLE_PERSONAS, 3, seed=99)
        # 우연히 같을 수 있으나, 5개 모집단에서 3개 sample 다른 seed 면 거의 다름
        # 결정적 검증은 어려우니 size 만 확인
        assert len(a) == 3 and len(b) == 3

    def test_sample_size_equals_population(self):
        result = sample_personas(SAMPLE_PERSONAS, 5, seed=42)
        assert len(result) == 5

    def test_sample_size_exceeds_population_returns_all(self):
        result = sample_personas(SAMPLE_PERSONAS, 100, seed=42)
        assert len(result) == 5
        assert {p.persona_id for p in result} == {p.persona_id for p in SAMPLE_PERSONAS}

    def test_sample_zero_raises(self):
        with pytest.raises(ValueError):
            sample_personas(SAMPLE_PERSONAS, 0, seed=42)

    def test_sample_negative_raises(self):
        with pytest.raises(ValueError):
            sample_personas(SAMPLE_PERSONAS, -1, seed=42)

    def test_results_sorted_by_persona_id(self):
        result = sample_personas(SAMPLE_PERSONAS, 3, seed=42)
        ids = [p.persona_id for p in result]
        assert ids == sorted(ids)


class TestFilterSummary:
    def test_no_filter(self):
        assert "전체" in filter_summary(PersonaFilter())

    def test_age_only(self):
        s = filter_summary(PersonaFilter(age_min=20, age_max=40))
        assert "20" in s and "40" in s

    def test_combined(self):
        s = filter_summary(
            PersonaFilter(age_min=30, sex=frozenset(["M"]), province=frozenset(["서울특별시"]))
        )
        assert "30" in s and "M" in s and "서울" in s


class TestOccupationCaseInsensitive:
    """occupation_contains 는 case-insensitive 부분 일치 (task instructions §2)."""

    def test_uppercase_keyword_matches_lowercase_occupation(self):
        p = _make("p1", 30, "F", occupation="교사")
        f = PersonaFilter(occupation_contains=frozenset(["교사"]))
        assert f.matches(p)

    def test_mixed_case_keyword_matches(self):
        p = _make("p1", 30, "M", occupation="IT Manager")
        f = PersonaFilter(occupation_contains=frozenset(["it"]))
        assert f.matches(p)

    def test_upper_occupation_lower_keyword_matches(self):
        p = _make("p1", 30, "M", occupation="DOCTOR")
        f = PersonaFilter(occupation_contains=frozenset(["doctor"]))
        assert f.matches(p)

    def test_partial_match_case_insensitive(self):
        p = _make("p1", 28, "F", occupation="소프트웨어 Engineer")
        f = PersonaFilter(occupation_contains=frozenset(["engineer"]))
        assert f.matches(p)

    def test_no_match_returns_false(self):
        p = _make("p1", 28, "F", occupation="교사")
        f = PersonaFilter(occupation_contains=frozenset(["의사"]))
        assert not f.matches(p)


class TestSampleToResult:
    """sample_to_result → SampleResult 검증."""

    def test_returns_sample_result_type(self):
        result = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        assert isinstance(result, SampleResult)

    def test_matched_count_reflects_input_size(self):
        result = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        assert result.matched_count_before_sample == len(SAMPLE_PERSONAS)

    def test_sample_size_reflects_requested(self):
        result = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        assert result.sample_size == 3
        assert len(result.rows) == 3

    def test_sample_size_exceeds_population_returns_all(self):
        result = sample_to_result(SAMPLE_PERSONAS, 100, seed=42)
        assert len(result.rows) == len(SAMPLE_PERSONAS)
        assert result.sample_size == len(SAMPLE_PERSONAS)

    def test_empty_population_returns_empty_result(self):
        result = sample_to_result([], 5, seed=42)
        assert result.rows == []
        assert result.matched_count_before_sample == 0
        assert result.sample_size == 0

    def test_seed_determinism(self):
        a = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        b = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        assert [p.persona_id for p in a.rows] == [p.persona_id for p in b.rows]

    def test_different_seeds_may_differ(self):
        a = sample_to_result(SAMPLE_PERSONAS, 3, seed=1)
        b = sample_to_result(SAMPLE_PERSONAS, 3, seed=999)
        # 다를 가능성이 높음 (5명 중 3명 샘플링)
        assert len(a.rows) == 3 and len(b.rows) == 3

    def test_sampling_seed_stored(self):
        result = sample_to_result(SAMPLE_PERSONAS, 3, seed=77)
        assert result.sampling_seed == 77

    def test_no_duplicate_in_sample(self):
        result = sample_to_result(SAMPLE_PERSONAS, 4, seed=42)
        ids = [p.persona_id for p in result.rows]
        assert len(ids) == len(set(ids))

    def test_negative_sample_size_raises(self):
        with pytest.raises(ValueError):
            sample_to_result(SAMPLE_PERSONAS, -1, seed=42)

    def test_zero_sample_size_raises(self):
        with pytest.raises(ValueError):
            sample_to_result(SAMPLE_PERSONAS, 0, seed=42)

    def test_results_sorted_by_persona_id(self):
        result = sample_to_result(SAMPLE_PERSONAS, 3, seed=42)
        ids = [p.persona_id for p in result.rows]
        assert ids == sorted(ids)


class TestSampleWithAgeAssist:
    def test_expands_age_range_once_when_original_matches_below_half(self):
        personas = [
            _make("p30a", 30, "F"),
            _make("p30b", 30, "F"),
            _make("p25a", 25, "F"),
            _make("p25b", 25, "F"),
            _make("p35a", 35, "F"),
            _make("p35b", 35, "F"),
            _make("p40", 40, "F"),
        ]

        result = sample_with_age_assist(
            personas,
            PersonaFilter(age_min=30, age_max=30),
            sample_size=10,
            seed=42,
        )

        assert result.age_assist_applied is True
        assert result.age_assist_original_matched_count == 2
        assert result.age_assist_expanded_matched_count == 6
        assert result.age_assist_expanded_age_min == 25
        assert result.age_assist_expanded_age_max == 35
        assert {p.persona_id for p in result.rows} == {
            "p25a",
            "p25b",
            "p30a",
            "p30b",
            "p35a",
            "p35b",
        }
        assert result.age_assist_sampled_count == 4
        assert result.age_assist_sampled_pct == pytest.approx(66.7)
        assert result.age_assist_underfilled_after_expansion is True

    def test_does_not_expand_when_original_matches_at_half(self):
        personas = [_make(f"p{i}", 30, "F") for i in range(5)] + [_make("near", 25, "F")]

        result = sample_with_age_assist(
            personas,
            PersonaFilter(age_min=30, age_max=30),
            sample_size=10,
            seed=42,
        )

        assert result.age_assist_applied is False
        assert {p.persona_id for p in result.rows} == {f"p{i}" for i in range(5)}
        assert result.sampling_diagnostics()["age_assist_original_matched_count"] == 5

    def test_does_not_expand_without_age_filter(self):
        result = sample_with_age_assist(
            SAMPLE_PERSONAS,
            PersonaFilter(sex=frozenset({"M"})),
            sample_size=10,
            seed=42,
        )

        assert result.age_assist_applied is False
        assert {p.persona_id for p in result.rows} == {"p3", "p4"}


class TestSampleIterableToResult:
    def test_seeded_reservoir_sampling_is_deterministic(self):
        personas = [_make(f"p{i}", 20 + i, "F") for i in range(10)]

        a = sample_iterable_to_result(iter(personas), PersonaFilter(), 3, seed=42)
        b = sample_iterable_to_result(iter(personas), PersonaFilter(), 3, seed=42)

        assert [p.persona_id for p in a.rows] == [p.persona_id for p in b.rows]
        assert a.matched_count_before_sample == 10
        assert a.sample_size == 3

    def test_seeded_reservoir_sampling_is_not_fixed_first_n(self):
        personas = [_make(f"p{i}", 20 + i, "F") for i in range(10)]

        result = sample_iterable_to_result(iter(personas), PersonaFilter(), 3, seed=42)

        assert [p.persona_id for p in result.rows] != ["p0", "p1", "p2"]

    def test_seed_affects_reservoir_sample(self):
        personas = [_make(f"p{i}", 20 + i, "F") for i in range(10)]

        seed_42 = sample_iterable_to_result(iter(personas), PersonaFilter(), 3, seed=42)
        seed_999 = sample_iterable_to_result(iter(personas), PersonaFilter(), 3, seed=999)

        assert [p.persona_id for p in seed_42.rows] != [p.persona_id for p in seed_999.rows]


class TestTakeMatchingIterableToResult:
    def test_takes_first_matching_rows_and_stops(self):
        personas = [_make(f"m{i}", 20 + i, "M") for i in range(5)] + [
            _make(f"f{i}", 25 + i, "F") for i in range(5)
        ]

        result = take_matching_iterable_to_result(
            iter(personas),
            PersonaFilter(sex=frozenset({"F"})),
            3,
            seed=42,
        )

        assert [p.persona_id for p in result.rows] == ["f0", "f1", "f2"]
        assert result.matched_count_before_sample == 3
        assert result.sample_size == 3
        assert result.sampling_seed == 42

    def test_returns_partial_when_stream_ends_before_target(self):
        personas = [_make("f0", 25, "F"), _make("m0", 30, "M")]

        result = take_matching_iterable_to_result(
            iter(personas),
            PersonaFilter(sex=frozenset({"F"})),
            3,
            seed=42,
        )

        assert [p.persona_id for p in result.rows] == ["f0"]
        assert result.matched_count_before_sample == 1
        assert result.sample_size == 1

    def test_zero_sample_size_raises(self):
        with pytest.raises(ValueError):
            take_matching_iterable_to_result(iter(SAMPLE_PERSONAS), PersonaFilter(), 0, seed=42)


class TestPreviewFirstN:
    """preview_first_n 함수 검증."""

    def test_returns_first_n_items(self):
        data = list(range(50))
        result = preview_first_n(data, n=30)
        assert result == list(range(30))

    def test_shorter_than_n_returns_all(self):
        data = list(range(10))
        result = preview_first_n(data, n=30)
        assert result == list(range(10))

    def test_default_n_is_30(self):
        data = list(range(100))
        result = preview_first_n(data)
        assert len(result) == 30

    def test_n_zero_returns_empty(self):
        data = list(range(10))
        result = preview_first_n(data, n=0)
        assert result == []

    def test_empty_input_returns_empty(self):
        result = preview_first_n([], n=30)
        assert result == []

    def test_works_with_persona_objects(self):
        result = preview_first_n(SAMPLE_PERSONAS, n=3)
        assert len(result) == 3
        assert all(isinstance(p, Persona) for p in result)
