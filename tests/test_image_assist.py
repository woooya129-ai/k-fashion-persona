from __future__ import annotations

import base64
import json

import pytest

from src.image_assist import (
    anthropic_image_analyzer,
    configured_image_analyzer_from_env,
    google_image_analyzer,
    image_analyzer_for_session,
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


def test_image_analyzer_for_session_selects_provider() -> None:
    openai = image_analyzer_for_session("openai", "k1", "gpt-vision")
    anthropic = image_analyzer_for_session("Anthropic", "k2", "claude-vision")
    google = image_analyzer_for_session("google", "k3", "gemini-vision")

    assert openai is not None and openai.func is openai_image_analyzer
    assert openai.keywords == {"api_key": "k1", "model": "gpt-vision"}
    assert anthropic is not None and anthropic.func is anthropic_image_analyzer
    assert google is not None and google.func is google_image_analyzer


def test_image_analyzer_for_session_none_cases() -> None:
    assert image_analyzer_for_session("openai", "", "model") is None
    assert image_analyzer_for_session("openai", "key", "") is None
    assert image_analyzer_for_session("openai", "   ", "model") is None
    assert image_analyzer_for_session("unsupported", "key", "model") is None
    assert image_analyzer_for_session("", "key", "model") is None


def test_anthropic_image_analyzer_returns_text_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"content": [{"type": "text", "text": "앤트로픽 초안"}]}

    def fake_post(url: str, *, headers: dict[str, str], json: dict, timeout: float) -> FakeResponse:
        calls.append({"url": url, "headers": headers, "json": json})
        return FakeResponse()

    monkeypatch.setattr("src.image_assist.httpx.post", fake_post)

    draft = anthropic_image_analyzer(
        image_bytes=b"image",
        mime_type="image/jpeg",
        prompt="초안",
        api_key="ak",
        model="claude-vision",
    )

    assert draft == "앤트로픽 초안"
    assert calls[0]["url"] == "https://api.anthropic.com/v1/messages"
    headers = calls[0]["headers"]
    assert isinstance(headers, dict)
    assert headers["x-api-key"] == "ak"
    assert headers["anthropic-version"] == "2023-06-01"
    payload = calls[0]["json"]
    assert isinstance(payload, dict)
    block = payload["messages"][0]["content"][0]
    assert block["type"] == "image"
    assert block["source"]["type"] == "base64"
    assert block["source"]["media_type"] == "image/jpeg"


def test_google_image_analyzer_returns_text_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"candidates": [{"content": {"parts": [{"text": "제미나이 초안"}]}}]}

    def fake_post(url: str, *, headers: dict[str, str], json: dict, timeout: float) -> FakeResponse:
        calls.append({"url": url, "headers": headers, "json": json})
        return FakeResponse()

    monkeypatch.setattr("src.image_assist.httpx.post", fake_post)

    draft = google_image_analyzer(
        image_bytes=b"image",
        mime_type="image/png",
        prompt="초안",
        api_key="gk",
        model="gemini-vision",
    )

    assert draft == "제미나이 초안"
    assert "models/gemini-vision:generateContent" in str(calls[0]["url"])
    headers = calls[0]["headers"]
    assert isinstance(headers, dict)
    assert headers["x-goog-api-key"] == "gk"
    payload = calls[0]["json"]
    assert isinstance(payload, dict)
    parts = payload["contents"][0]["parts"]
    assert any("inline_data" in p for p in parts)


def test_session_analyzer_drives_make_image_concept_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"content": [{"type": "text", "text": "세션 키 기반 초안"}]}

    monkeypatch.setattr("src.image_assist.httpx.post", lambda *a, **k: FakeResponse())

    analyzer = image_analyzer_for_session("anthropic", "session-key", "claude-vision")
    assert analyzer is not None

    draft = make_image_concept_draft(
        image_bytes=b"image-bytes",
        mime_type="image/png",
        analyzer=analyzer,
    )
    assert draft == "세션 키 기반 초안"


def test_concept_update_never_leaks_image_or_vision_bytes() -> None:
    """SAFETY INVARIANT: only normalized description text may flow forward."""
    image_b64 = base64.b64encode(b"\x89PNG raw image bytes").decode("ascii")
    raw_vision_response = json.dumps(
        {"content": [{"type": "image", "source": {"data": image_b64}}]}
    )

    # The draft is plain text; only that text is allowed downstream.
    update = image_assist_concept_update("미니멀 니트 초안")

    assert set(update) == {"description"}
    assert update["description"] == "미니멀 니트 초안"
    serialized = json.dumps(update, ensure_ascii=False)
    assert image_b64 not in serialized
    assert "base64" not in serialized
    assert raw_vision_response not in serialized
    assert "image_bytes" not in serialized
    assert b"\x89PNG".decode("latin-1") not in serialized
