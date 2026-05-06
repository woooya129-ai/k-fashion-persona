import copy

import pytest

from src.persona_normalizer import Persona, normalize_persona
from tests.fixtures.mock_personas import (
    MOCK_PERSONA_1,
    MOCK_PERSONA_2,
    MOCK_PERSONA_3,
)

pytestmark = pytest.mark.no_network


class TestNormalizePersonaHappyPath:
    @pytest.mark.parametrize(
        "raw, row_id",
        [
            (MOCK_PERSONA_1, 0),
            (MOCK_PERSONA_2, 1),
            (MOCK_PERSONA_3, 2),
        ],
    )
    def test_all_mock_personas_return_persona_object(self, raw, row_id):
        result = normalize_persona(raw, row_id)
        assert result is not None
        assert isinstance(result, Persona)

    def test_persona_id_maps_from_uuid(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        assert result.persona_id == MOCK_PERSONA_1["uuid"]

    def test_age_maps_to_int(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        assert result.age == 25
        assert isinstance(result.age, int)

    def test_sex_maps_correctly(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        assert result.sex == "F"

    def test_persona_maps_to_persona_summary(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        assert result.persona_summary == MOCK_PERSONA_1["persona"]

    def test_province_and_district_map(self):
        result = normalize_persona(MOCK_PERSONA_2, 1)
        assert result is not None
        assert result.province == "부산광역시"
        assert result.district == "해운대구"

    def test_occupation_maps(self):
        result = normalize_persona(MOCK_PERSONA_3, 2)
        assert result is not None
        assert result.occupation == "중학교 교사"

    def test_source_row_id_stored(self):
        result = normalize_persona(MOCK_PERSONA_1, 7)
        assert result is not None
        assert result.source_row_id == 7

    def test_lifestyle_text_concat_separator(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        expected = MOCK_PERSONA_1["cultural_background"] + "\n\n" + MOCK_PERSONA_1["family_persona"]
        assert result.lifestyle_text == expected

    def test_interests_text_concat_separator(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        parts = [
            MOCK_PERSONA_1["hobbies_and_interests"],
            MOCK_PERSONA_1["sports_persona"],
            MOCK_PERSONA_1["arts_persona"],
            MOCK_PERSONA_1["travel_persona"],
            MOCK_PERSONA_1["culinary_persona"],
        ]
        expected = "\n\n".join(p for p in parts if p)
        assert result.interests_text == expected

    def test_professional_text_maps_from_professional_persona(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        assert result.professional_text == MOCK_PERSONA_1["professional_persona"]

    def test_persona_is_frozen(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        with pytest.raises((AttributeError, TypeError)):
            result.age = 99  # type: ignore[misc]


class TestNormalizePersonaRequiredFieldsMissing:
    def test_missing_uuid_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["uuid"]
        assert normalize_persona(raw, 0) is None

    def test_empty_uuid_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["uuid"] = ""
        assert normalize_persona(raw, 0) is None

    def test_none_uuid_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["uuid"] = None
        assert normalize_persona(raw, 0) is None

    def test_missing_age_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["age"]
        assert normalize_persona(raw, 0) is None

    def test_non_castable_age_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["age"] = "스물다섯"
        assert normalize_persona(raw, 0) is None

    def test_none_age_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["age"] = None
        assert normalize_persona(raw, 0) is None

    def test_missing_sex_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["sex"]
        assert normalize_persona(raw, 0) is None

    def test_empty_sex_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["sex"] = ""
        assert normalize_persona(raw, 0) is None

    def test_missing_persona_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["persona"]
        assert normalize_persona(raw, 0) is None

    def test_empty_persona_returns_none(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["persona"] = ""
        assert normalize_persona(raw, 0) is None


class TestNormalizePersonaOptionalFieldsMissing:
    def test_missing_district_becomes_empty_string(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["district"]
        result = normalize_persona(raw, 0)
        assert result is not None
        assert result.district == ""

    def test_none_occupation_becomes_empty_string(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["occupation"] = None
        result = normalize_persona(raw, 0)
        assert result is not None
        assert result.occupation == ""

    def test_missing_optional_does_not_use_sentinel(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        del raw["housing_type"]
        result = normalize_persona(raw, 0)
        assert result is not None
        assert result.housing_type == ""
        assert result.housing_type != "(unknown)"
        assert result.housing_type != "N/A"
        assert result.housing_type != "unknown"


class TestNormalizePersonaConcatEdgeCases:
    def test_lifestyle_text_with_one_empty_part_no_leading_separator(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["cultural_background"] = ""
        result = normalize_persona(raw, 0)
        assert result is not None
        assert result.lifestyle_text == MOCK_PERSONA_1["family_persona"]
        assert not result.lifestyle_text.startswith("\n\n")

    def test_interests_text_with_missing_sports_persona(self):
        raw = copy.deepcopy(MOCK_PERSONA_1)
        raw["sports_persona"] = ""
        result = normalize_persona(raw, 0)
        assert result is not None
        assert "\n\n\n\n" not in result.interests_text


class TestNormalizePersonaV01UnusedFields:
    def test_unused_fields_not_in_persona_object(self):
        result = normalize_persona(MOCK_PERSONA_1, 0)
        assert result is not None
        unused = [
            "country",
            "military_status",
            "bachelors_field",
            "skills_and_expertise",
            "skills_and_expertise_list",
            "hobbies_and_interests_list",
            "career_goals_and_ambitions",
        ]
        for field in unused:
            assert not hasattr(result, field), f"Persona should not have field: {field}"
