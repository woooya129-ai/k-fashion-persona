# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json

import pytest

from src.concept_parser import (
    ALLOWED_FIELDS,
    ConceptDraft,
    parse_concept_text,
)

pytestmark = pytest.mark.no_network


def _mock_returning(text: str):
    calls: list[str] = []

    def _call(prompt: str) -> str:
        calls.append(prompt)
        return text

    _call.calls = calls  # type: ignore[attr-defined]
    return _call


def test_success_parse_extracts_whitelisted_fields() -> None:
    payload = {
        "category": "니트",
        "fit": "오버핏",
        "material": "울 혼방",
        "color": "차콜",
        "design_details": ["라운드넥", "리브 밑단"],
        "season": "가을",
        "occasion": "데일리",
        "style_tone": "미니멀",
        "target_hypothesis": "20대 직장인",
        "description": "차콜 컬러의 오버핏 울 혼방 니트.",
    }
    llm_call = _mock_returning(json.dumps(payload, ensure_ascii=False))

    draft = parse_concept_text("오버핏 울 니트, 차콜 컬러", llm_call=llm_call)

    assert isinstance(draft, ConceptDraft)
    assert draft.fallback_description_only is False
    assert draft.fields["category"] == "니트"
    assert draft.fields["design_details"] == ["라운드넥", "리브 밑단"]
    assert set(draft.fields).issubset(set(ALLOWED_FIELDS))
    # The raw product text is forwarded inside the prompt.
    assert "오버핏 울 니트" in llm_call.calls[0]  # type: ignore[attr-defined]


def test_code_fence_stripping() -> None:
    payload = {"category": "코트", "color": "베이지"}
    body = json.dumps(payload, ensure_ascii=False)
    fenced = f"여기 결과입니다:\n```json\n{body}\n```\n감사합니다."
    llm_call = _mock_returning(fenced)

    draft = parse_concept_text("베이지 코트", llm_call=llm_call)

    assert draft.fallback_description_only is False
    assert draft.fields["category"] == "코트"
    assert draft.fields["color"] == "베이지"


def test_leading_trailing_prose_without_fence() -> None:
    payload = {"category": "셔츠"}
    text = f"분석 결과는 다음과 같습니다 {json.dumps(payload, ensure_ascii=False)} 이상입니다"
    draft = parse_concept_text("흰 셔츠", llm_call=_mock_returning(text))

    assert draft.fallback_description_only is False
    assert draft.fields["category"] == "셔츠"


def test_total_failure_falls_back_to_description_only() -> None:
    llm_call = _mock_returning("죄송합니다. JSON을 만들 수 없습니다.")

    raw = "  오버핏   니트\n\n  차콜 컬러  "
    draft = parse_concept_text(raw, llm_call=llm_call)

    assert draft.fallback_description_only is True
    assert set(draft.fields) == {"description"}
    # Normalized: intra-line whitespace collapsed, blank lines dropped.
    assert draft.fields["description"] == "오버핏 니트\n차콜 컬러"


def test_non_whitelisted_keys_are_dropped() -> None:
    payload = {
        "category": "원피스",
        "evaluation": "인기가 많을 것",
        "reaction_prediction": "구매율 높음",
        "random_key": "x",
        "design_details": "단일값",
    }
    llm_call = _mock_returning(json.dumps(payload, ensure_ascii=False))

    draft = parse_concept_text("원피스", llm_call=llm_call)

    assert draft.fallback_description_only is False
    assert "evaluation" not in draft.fields
    assert "reaction_prediction" not in draft.fields
    assert "random_key" not in draft.fields
    assert draft.fields["category"] == "원피스"
    # A scalar value for a list field is coerced into a single-item list.
    assert draft.fields["design_details"] == ["단일값"]


def test_empty_response_falls_back() -> None:
    draft = parse_concept_text("티셔츠", llm_call=_mock_returning(""))
    assert draft.fallback_description_only is True
    assert draft.fields == {"description": "티셔츠"}
