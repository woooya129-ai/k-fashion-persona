from __future__ import annotations

import pytest

from src.image_assist import (
    configured_image_analyzer_from_env,
    image_assist_concept_update,
    make_image_concept_draft,
    openai_image_analyzer,
)

pytestmark = pytest.mark.no_network


def test_make_image_concept_draft_calls_analyzer_once() -> None:
    calls: list[dict[str, object]] = []

    def analyzer(**kwargs: object) -> str:
        calls.append(kwargs)
        return "미니멀 니트웨어 초안"

    draft = make_image_concept_draft(
        image_bytes=b"image-bytes",
        mime_type="image/png",
        current_description="기존 설명",
        analyzer=analyzer,
    )

    assert draft == "미니멀 니트웨어 초안"
    assert len(calls) == 1
    assert calls[0]["image_bytes"] == b"image-bytes"
    assert calls[0]["mime_type"] == "image/png"
    assert "기존 설명" in str(calls[0]["prompt"])


def test_make_image_concept_draft_rejects_empty_image() -> None:
    with pytest.raises(ValueError, match="empty"):
        make_image_concept_draft(
            image_bytes=b"",
            mime_type="image/png",
            analyzer=lambda **_: "draft",
        )


def test_image_assist_concept_update_contains_only_text() -> None:
    update = image_assist_concept_update("  설명 초안\n\n")

    assert update == {"description": "설명 초안"}
    assert "image_bytes" not in update
    assert "vision_raw_response" not in update


def test_configured_image_analyzer_requires_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "fake")
    monkeypatch.delenv("KFPS_IMAGE_ASSIST_MODEL", raising=False)

    assert configured_image_analyzer_from_env() is None


def test_openai_image_analyzer_returns_text_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "이미지 기반 초안"}}]}

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        json: dict,
        timeout: float,
    ) -> FakeResponse:
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("src.image_assist.httpx.post", fake_post)

    draft = openai_image_analyzer(
        image_bytes=b"image",
        mime_type="image/png",
        prompt="초안",
        api_key="fake-key",
        model="vision-model",
    )

    assert draft == "이미지 기반 초안"
    assert len(calls) == 1
    payload = calls[0]["json"]
    assert isinstance(payload, dict)
    assert payload["model"] == "vision-model"
    assert "data:image/png;base64," in str(payload)
    assert calls[0]["headers"] == {
        "Authorization": "Bearer fake-key",
        "Content-Type": "application/json",
    }
