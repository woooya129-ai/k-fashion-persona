# SPDX-License-Identifier: AGPL-3.0-only
"""API key / HF token 로딩.

Runtime credential policy:
- 실제 키는 ~/secrets/k-fashion/.env (프로젝트 root 밖)
- 코드에 키 직접 작성 금지
- print/log 에 키 출력 금지 (일부라도)
- 에러 메시지에 키 노출 금지
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv 미설치 환경에서도 모듈 import 가능
    load_dotenv = None  # type: ignore[assignment]


SECRETS_ENV_PATH: Path = Path.home() / "secrets" / "k-fashion" / ".env"

# 아래 상수는 환경변수 *이름* 이며 실제 자격증명 값이 아니다.
# bandit B105 hardcoded_password_string false-positive 회피.
OPENAI_KEY_VAR = "OPENAI_API_KEY"
ANTHROPIC_KEY_VAR = "ANTHROPIC_API_KEY"
GOOGLE_KEY_VAR = "GOOGLE_API_KEY"
GROQ_KEY_VAR = "GROQ_API_KEY"
DEEPSEEK_KEY_VAR = "DEEPSEEK_API_KEY"
QWEN_KEY_VAR = "QWEN_API_KEY"
HF_TOKEN_VAR = "HF_TOKEN"
KOSIS_API_KEY_VAR = "KOSIS_API_KEY"
DATAGOKR_SERVICE_KEY_VAR = "DATAGOKR_SERVICE_KEY"
SGIS_CONSUMER_KEY_VAR = "SGIS_CONSUMER_KEY"
SGIS_CONSUMER_SECRET_VAR = "SGIS_CONSUMER_SECRET"
KMA_APIHUB_AUTH_KEY_VAR = "KMA_APIHUB_AUTH_KEY"
REQUIRE_USER_PROVIDER_KEY_VAR = "KFPS_REQUIRE_USER_PROVIDER_KEY"

_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class LoadedSecretsStatus:
    """자격증명 보유 여부만 노출. 실제 값은 절대 포함하지 않음."""

    openai_present: bool
    anthropic_present: bool
    hf_token_present: bool
    env_path: Path
    env_path_exists: bool
    google_present: bool = False
    groq_present: bool = False
    deepseek_present: bool = False
    qwen_present: bool = False
    kosis_api_key_present: bool = False
    datagokr_service_key_present: bool = False
    sgis_consumer_key_present: bool = False
    sgis_consumer_secret_present: bool = False
    kma_apihub_auth_key_present: bool = False


def load_secrets_from_env_path(env_path: Path = SECRETS_ENV_PATH) -> LoadedSecretsStatus:
    """~/secrets/k-fashion/.env → os.environ 로딩 + 보유 상태 반환.

    값 자체는 반환 또는 출력 금지. 호출자는 os.environ.get() 으로 직접 조회.
    파일 없어도 예외 발생 안 함 (사용자가 .env 작성 안 했을 수 있음 — UI 에서 안내).
    """
    env_path = Path(env_path)
    exists = env_path.is_file()

    if exists and load_dotenv is not None:
        load_dotenv(env_path, override=False)

    provider_env_allowed = provider_env_fallback_allowed()

    return LoadedSecretsStatus(
        openai_present=provider_env_allowed and bool(os.environ.get(OPENAI_KEY_VAR)),
        anthropic_present=provider_env_allowed and bool(os.environ.get(ANTHROPIC_KEY_VAR)),
        hf_token_present=bool(os.environ.get(HF_TOKEN_VAR)),
        env_path=env_path,
        env_path_exists=exists,
        google_present=provider_env_allowed and bool(os.environ.get(GOOGLE_KEY_VAR)),
        groq_present=provider_env_allowed and bool(os.environ.get(GROQ_KEY_VAR)),
        deepseek_present=provider_env_allowed and bool(os.environ.get(DEEPSEEK_KEY_VAR)),
        qwen_present=provider_env_allowed and bool(os.environ.get(QWEN_KEY_VAR)),
        kosis_api_key_present=bool(os.environ.get(KOSIS_API_KEY_VAR)),
        datagokr_service_key_present=bool(os.environ.get(DATAGOKR_SERVICE_KEY_VAR)),
        sgis_consumer_key_present=bool(os.environ.get(SGIS_CONSUMER_KEY_VAR)),
        sgis_consumer_secret_present=bool(os.environ.get(SGIS_CONSUMER_SECRET_VAR)),
        kma_apihub_auth_key_present=bool(os.environ.get(KMA_APIHUB_AUTH_KEY_VAR)),
    )


def require_user_provider_key() -> bool:
    """공유 배포에서 provider env key fallback을 끌지 여부."""
    return os.environ.get(REQUIRE_USER_PROVIDER_KEY_VAR, "").strip().lower() in _TRUE_VALUES


def provider_env_fallback_allowed() -> bool:
    """LLM provider key를 env에서 읽어도 되는지 반환."""
    return not require_user_provider_key()


def get_provider_key(
    provider: str,
    api_key_env: str | None = None,
    *,
    allow_env_fallback: bool | None = None,
) -> str | None:
    """provider 이름 또는 명시 env var → 환경변수 값."""
    if allow_env_fallback is None:
        allow_env_fallback = provider_env_fallback_allowed()

    if not allow_env_fallback:
        return None

    if api_key_env:
        val = os.environ.get(api_key_env)
        return val if val else None

    mapping = {
        "openai": OPENAI_KEY_VAR,
        "anthropic": ANTHROPIC_KEY_VAR,
        "google": GOOGLE_KEY_VAR,
        "groq": GROQ_KEY_VAR,
        "deepseek": DEEPSEEK_KEY_VAR,
        "qwen": QWEN_KEY_VAR,
    }
    var = mapping.get(provider.lower())
    if var is None:
        raise ValueError(f"unknown provider: {provider}")
    val = os.environ.get(var)
    return val if val else None


def get_hf_token() -> str | None:
    val = os.environ.get(HF_TOKEN_VAR)
    return val if val else None


def get_kosis_api_key() -> str | None:
    val = os.environ.get(KOSIS_API_KEY_VAR)
    return val if val else None


def get_datagokr_service_key() -> str | None:
    val = os.environ.get(DATAGOKR_SERVICE_KEY_VAR)
    return val if val else None


def get_sgis_consumer_key() -> str | None:
    val = os.environ.get(SGIS_CONSUMER_KEY_VAR)
    return val if val else None


def get_sgis_consumer_secret() -> str | None:
    val = os.environ.get(SGIS_CONSUMER_SECRET_VAR)
    return val if val else None


def get_kma_apihub_auth_key() -> str | None:
    val = os.environ.get(KMA_APIHUB_AUTH_KEY_VAR)
    return val if val else None


def redact_for_log(secret: str | None, keep: int = 0) -> str:
    """로그 출력용 redaction. keep > 0 이어도 최대 0자 (Hard Rule §2: 일부라도 출력 금지).

    None / 빈 문자열 → [ABSENT] (load_secrets 의 absent 의미와 동일).
    그 외 → [REDACTED]. keep 인자는 호출자 의도 명확화 용도.
    """
    if not secret:
        return "[ABSENT]"
    return "[REDACTED]"
