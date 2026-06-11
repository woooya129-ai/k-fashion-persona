# SPDX-License-Identifier: AGPL-3.0-only
"""Image-to-concept draft helper.

This module defines the call boundary for the optional image assist feature.
It returns editable text only; raw image bytes and raw vision responses must
not enter persona evaluation payloads, reports, logs, or persisted snapshots.
"""

import base64
import os
import unicodedata
from collections.abc import Callable
from functools import partial
from typing import Any

import httpx

ImageAnalyzer = Callable[..., str]

MAX_IMAGE_ASSIST_BYTES = 5 * 1024 * 1024
IMAGE_ASSIST_PROVIDER_VAR = "KFPS_IMAGE_ASSIST_PROVIDER"
IMAGE_ASSIST_MODEL_VAR = "KFPS_IMAGE_ASSIST_MODEL"
OPENAI_API_KEY_VAR = "OPENAI_API_KEY"
SUPPORTED_IMAGE_ASSIST_PROVIDERS: frozenset[str] = frozenset(
    {"openai", "anthropic", "google"}
)
IMAGE_ASSIST_PROMPT = (
    "패션 제품 이미지를 보고 브랜드 메시지/제품 설명 초안을 한국어로 작성해. "
    "평가나 반응 예측은 하지 말고, 눈에 보이는 카테고리, 핏, 소재감, 컬러, "
    "디자인 디테일, 착용 상황 가설만 간결하게 정리해."
)
_OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"
_GOOGLE_GENERATE_CONTENT_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


def normalize_image_assist_draft(value: object) -> str:
    text = unicodedata.normalize("NFC", str(value or ""))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()


def make_image_concept_draft(
    *,
    image_bytes: bytes,
    mime_type: str,
    current_description: str = "",
    analyzer: ImageAnalyzer,
) -> str:
    """Return one editable concept draft from one image and one analyzer call."""
    if not image_bytes:
        raise ValueError("image_bytes is empty")
    if len(image_bytes) > MAX_IMAGE_ASSIST_BYTES:
        raise ValueError("image_bytes exceeds the image assist size limit")
    prompt = IMAGE_ASSIST_PROMPT
    current = normalize_image_assist_draft(current_description)
    if current:
        prompt += f"\n\n기존 사용자가 적은 설명:\n{current}"
    draft = normalize_image_assist_draft(
        analyzer(image_bytes=image_bytes, mime_type=mime_type, prompt=prompt)
    )
    if not draft:
        raise ValueError("image analyzer returned an empty draft")
    return draft


def image_assist_concept_update(draft: str) -> dict[str, str]:
    """Return the only data allowed to flow into concept input state."""
    return {"description": normalize_image_assist_draft(draft)}


def openai_image_analyzer(
    *,
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
    api_key: str,
    model: str,
    timeout: float = 60.0,
) -> str:
    """Call OpenAI for one image-description draft and return text only."""
    if not api_key.strip() or not model.strip():
        raise ValueError("OpenAI image assist requires api_key and model")
    media_type = mime_type.strip() or "image/png"
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{media_type};base64,{image_b64}"},
                    },
                ],
            }
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }
    response = httpx.post(
        _OPENAI_CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json()
    try:
        return str(body["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("OpenAI image assist response did not include text content") from exc


def anthropic_image_analyzer(
    *,
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
    api_key: str,
    model: str,
    timeout: float = 60.0,
) -> str:
    """Call Anthropic for one image-description draft and return text only."""
    if not api_key.strip() or not model.strip():
        raise ValueError("Anthropic image assist requires api_key and model")
    media_type = mime_type.strip() or "image/png"
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": 400,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }
    response = httpx.post(
        _ANTHROPIC_MESSAGES_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json()
    try:
        return str(body["content"][0]["text"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Anthropic image assist response did not include text content") from exc


def google_image_analyzer(
    *,
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
    api_key: str,
    model: str,
    timeout: float = 60.0,
) -> str:
    """Call Google Gemini for one image-description draft and return text only."""
    if not api_key.strip() or not model.strip():
        raise ValueError("Google image assist requires api_key and model")
    media_type = mime_type.strip() or "image/png"
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    payload: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": media_type, "data": image_b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 400},
    }
    response = httpx.post(
        _GOOGLE_GENERATE_CONTENT_URL.format(model=model),
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json()
    try:
        return str(body["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Google image assist response did not include text content") from exc


_SESSION_ANALYZERS: dict[str, ImageAnalyzer] = {
    "openai": openai_image_analyzer,
    "anthropic": anthropic_image_analyzer,
    "google": google_image_analyzer,
}


def image_analyzer_for_session(
    provider: str, api_key: str, model: str
) -> ImageAnalyzer | None:
    """Return an analyzer bound to a session-provided key, or None if unusable.

    Uses the key the user already typed in the UI session instead of the
    environment. Returns None for unsupported providers or missing key/model so
    callers can degrade gracefully without exposing secrets.
    """
    normalized_provider = (provider or "").strip().lower()
    analyzer = _SESSION_ANALYZERS.get(normalized_provider)
    if analyzer is None:
        return None
    if not api_key.strip() or not model.strip():
        return None
    return partial(analyzer, api_key=api_key, model=model)


def configured_image_analyzer_from_env() -> ImageAnalyzer | None:
    """Return an optional configured analyzer without exposing secrets."""
    provider = os.environ.get(IMAGE_ASSIST_PROVIDER_VAR, "openai").strip().lower()
    if provider != "openai":
        return None
    api_key = os.environ.get(OPENAI_API_KEY_VAR, "").strip()
    model = os.environ.get(IMAGE_ASSIST_MODEL_VAR, "").strip()
    if not api_key or not model:
        return None
    return partial(openai_image_analyzer, api_key=api_key, model=model)
