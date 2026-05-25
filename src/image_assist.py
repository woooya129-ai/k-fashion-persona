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
IMAGE_ASSIST_PROMPT = (
    "패션 제품 이미지를 보고 브랜드 메시지/제품 설명 초안을 한국어로 작성해. "
    "평가나 반응 예측은 하지 말고, 눈에 보이는 카테고리, 핏, 소재감, 컬러, "
    "디자인 디테일, 착용 상황 가설만 간결하게 정리해."
)
_OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


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
