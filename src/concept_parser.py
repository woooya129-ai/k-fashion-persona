# SPDX-License-Identifier: AGPL-3.0-only
"""Free-form Korean product text to structured concept-draft parser.

This module defines the call boundary for the optional concept-parse feature.
Text goes in, editable structured text comes out. Nothing here auto-flows into
persona evaluation: the parsed fields are an editable draft for the user, never
an evaluation payload, and the model is instructed to extract only factual,
observable product attributes (no evaluation, no reaction prediction).
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

# Whitelisted output keys. Anything else the model returns is dropped silently.
_LIST_FIELDS: frozenset[str] = frozenset({"design_details"})
ALLOWED_FIELDS: tuple[str, ...] = (
    "category",
    "fit",
    "material",
    "color",
    "design_details",
    "season",
    "occasion",
    "style_tone",
    "target_hypothesis",
    "description",
)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", re.IGNORECASE)

CONCEPT_PARSE_PROMPT = (
    "다음은 패션 제품에 대한 자유 형식의 한국어 설명이다. "
    "사실 정보만 추출해서 아래 키를 가진 JSON 객체 하나만 출력해라.\n\n"
    "키 목록: category, fit, material, color, design_details, season, "
    "occasion, style_tone, target_hypothesis, description\n\n"
    "규칙:\n"
    "- design_details 는 문자열 리스트, 나머지는 모두 문자열이다.\n"
    "- 광고 문구, 과장, 감탄사는 모두 제거하고 객관적인 정보만 남겨라.\n"
    "- 평가나 반응 예측(예: '인기가 많을 것', '소비자가 좋아할')은 절대 하지 마라.\n"
    "- 원문에서 알 수 없는 필드는 빈 문자열(\"\") 또는 빈 리스트([])로 둬라.\n"
    "- description 에는 사실 위주로 정리한 간결한 제품 설명을 한국어로 적어라.\n"
    "- JSON 외의 다른 텍스트는 출력하지 마라.\n\n"
    "원문:\n"
)


@dataclass(frozen=True)
class ConceptDraft:
    """An editable, structured concept draft derived from free-form text.

    fields contains only whitelisted keys. fallback_description_only is True
    when JSON parsing failed and only the normalized raw text is preserved.
    """

    fields: dict[str, str | list[str]]
    fallback_description_only: bool


def _normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFC", str(value or ""))
    return " ".join(text.split()).strip()


def _normalize_block(value: object) -> str:
    """Normalize multi-line text, collapsing intra-line whitespace per line."""
    text = unicodedata.normalize("NFC", str(value or ""))
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _coerce_field(key: str, value: object) -> str | list[str]:
    if key in _LIST_FIELDS:
        if isinstance(value, str):
            items = [value]
        elif isinstance(value, (list, tuple)):
            items = list(value)
        else:
            return []
        return [norm for item in items if (norm := _normalize_text(item))]
    return _normalize_text(value)


def _whitelist_fields(parsed: dict) -> dict[str, str | list[str]]:
    fields: dict[str, str | list[str]] = {}
    for key in ALLOWED_FIELDS:
        if key in parsed:
            fields[key] = _coerce_field(key, parsed[key])
    return fields


def _strip_fences(text: str) -> list[str]:
    return [m.group(1).strip() for m in _JSON_FENCE_RE.finditer(text)]


def _extract_first_object(text: str) -> str | None:
    """Return the first balanced top-level {...} block, ignoring strings."""
    start: int | None = None
    depth = 0
    in_string = False
    escaped = False
    for idx, char in enumerate(text):
        if start is None:
            if char == "{":
                start = idx
                depth = 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _load_object(text: str) -> dict | None:
    try:
        obj = json.loads(text.strip().lstrip("﻿"))
    except (json.JSONDecodeError, ValueError, TypeError):
        return None
    return obj if isinstance(obj, dict) else None


def _try_parse_json(raw_response: str) -> dict | None:
    candidates: list[str] = [raw_response, *_strip_fences(raw_response)]
    extracted = _extract_first_object(raw_response)
    if extracted is not None:
        candidates.append(extracted)
    for candidate in candidates:
        if not candidate.strip():
            continue
        parsed = _load_object(candidate)
        if parsed is not None:
            return parsed
    return None


def parse_concept_text(raw_text: str, *, llm_call: Callable[[str], str]) -> ConceptDraft:
    """Parse free-form Korean product text into an editable structured draft.

    llm_call takes the full prompt string and returns the model's raw text. The
    caller injects it so the LLM client never has to be built inside the parser.
    On any JSON parse failure, falls back to description-only with the normalized
    raw text preserved.
    """
    normalized_raw = _normalize_block(raw_text)
    prompt = f"{CONCEPT_PARSE_PROMPT}{normalized_raw}"

    raw_response = llm_call(prompt)
    parsed = _try_parse_json(raw_response or "")

    if parsed is None:
        return ConceptDraft(
            fields={"description": normalized_raw},
            fallback_description_only=True,
        )

    fields = _whitelist_fields(parsed)
    return ConceptDraft(fields=fields, fallback_description_only=False)


def build_concept_llm_call(provider: str, model: str, api_key: str) -> Callable[[str], str]:
    """Build a synchronous llm_call for parse_concept_text from llm_client.

    Bridges parse_concept_text's simple prompt->text contract onto the existing
    async LLMRequest/adapter path in src.llm_client. Vision is not used; this is
    a plain text completion. Structured-output flags are left off so the raw text
    (which parse_concept_text re-parses itself) is returned verbatim.
    """
    import asyncio

    import httpx

    from src.llm_client import LLMRequest, call_with_retry

    if not provider.strip() or not model.strip() or not api_key.strip():
        raise ValueError("build_concept_llm_call requires provider, model, and api_key")

    def _call(prompt: str) -> str:
        request = LLMRequest(
            provider=provider,  # type: ignore[arg-type]
            model_name=model,
            api_key=api_key,
            system="You extract factual fashion product attributes as JSON. No evaluation.",
            developer=None,
            user=prompt,
            temperature=0.2,
            supports_json_object=False,
            supports_json_schema=False,
            supports_tool_use=False,
        )

        async def _run() -> str:
            async with httpx.AsyncClient() as client:
                response = await call_with_retry(request, client)
                return response.text

        return asyncio.run(_run())

    return _call
