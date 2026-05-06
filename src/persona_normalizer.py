# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Persona:
    persona_id: str
    age: int
    sex: str
    province: str
    district: str
    occupation: str
    marital_status: str
    family_type: str
    housing_type: str
    education_level: str

    persona_summary: str
    professional_text: str
    lifestyle_text: str
    interests_text: str

    source_row_id: int


def _get_str(raw: dict, key: str) -> str:
    val = raw.get(key)
    if val is None:
        return ""
    return str(val).strip()


def _concat(*parts: str) -> str:
    return "\n\n".join(p for p in parts if p)


def normalize_persona(raw_row: dict, source_row_id: int) -> Persona | None:
    """26개 컬럼 raw row → 표준 Persona 객체.

    lock-in §1.3 매핑 규칙:
    - 필수 필드 (uuid, age, sex, persona) 누락 또는 캐스팅 실패 → None
    - 선택 필드 누락 → 빈 문자열 (sentinel 금지)
    - concat 구분자: "\n\n"
    - lifestyle_text  = cultural_background + family_persona
    - interests_text  = hobbies_and_interests + sports_persona + arts_persona
                        + travel_persona + culinary_persona
    - country / military_status / bachelors_field / skills_and_expertise(_list) /
      hobbies_and_interests_list / career_goals_and_ambitions 는 v0.1 미사용
    """
    persona_id = _get_str(raw_row, "uuid")
    if not persona_id:
        return None

    raw_sex = _get_str(raw_row, "sex")
    if not raw_sex:
        return None

    raw_persona = _get_str(raw_row, "persona")
    if not raw_persona:
        return None

    raw_age = raw_row.get("age")
    try:
        age = int(raw_age)
    except (TypeError, ValueError):
        return None

    lifestyle_text = _concat(
        _get_str(raw_row, "cultural_background"),
        _get_str(raw_row, "family_persona"),
    )
    interests_text = _concat(
        _get_str(raw_row, "hobbies_and_interests"),
        _get_str(raw_row, "sports_persona"),
        _get_str(raw_row, "arts_persona"),
        _get_str(raw_row, "travel_persona"),
        _get_str(raw_row, "culinary_persona"),
    )

    return Persona(
        persona_id=persona_id,
        age=age,
        sex=raw_sex,
        province=_get_str(raw_row, "province"),
        district=_get_str(raw_row, "district"),
        occupation=_get_str(raw_row, "occupation"),
        marital_status=_get_str(raw_row, "marital_status"),
        family_type=_get_str(raw_row, "family_type"),
        housing_type=_get_str(raw_row, "housing_type"),
        education_level=_get_str(raw_row, "education_level"),
        persona_summary=raw_persona,
        professional_text=_get_str(raw_row, "professional_persona"),
        lifestyle_text=lifestyle_text,
        interests_text=interests_text,
        source_row_id=source_row_id,
    )
