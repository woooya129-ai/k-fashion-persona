import tomllib
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.no_network

DOC_PATHS = (
    Path("README.md"),
    Path("docs/README-ENG.md"),
    Path("docs/INSTALL.md"),
    Path("docs/INSTALL-ENG.md"),
)


def _doc_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in DOC_PATHS)


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_docs_do_not_limit_api_keys_to_three_providers():
    text = _doc_text()
    blocked = (
        "OpenAI, Anthropic, Gemini API key",
        "OpenAI, Anthropic, or Gemini API keys",
        "OpenAI / Anthropic / Google Gemini",
        "selected OpenAI, Anthropic, or Gemini API server",
    )
    for phrase in blocked:
        assert phrase not in text


def test_docs_state_local_runtime_and_external_transfer_scope():
    readme_kr = _read("README.md")
    readme_en = _read("docs/README-ENG.md")
    install_kr = _read("docs/INSTALL.md")
    install_en = _read("docs/INSTALL-ENG.md")

    assert "SQLite 캐시" in readme_kr
    assert "사용자 PC에서 로컬로 실행" in readme_kr
    assert "선택한 provider API 서버로 프롬프트를 전송" in readme_kr
    assert "API key는 앱이 저장하지 않습니다" in readme_kr
    assert "The app does not save API keys" in readme_en
    assert "LLM provider API key" in install_kr
    assert "provider API key" in install_en


def test_docs_state_config_based_endpoint_allowlist_risk():
    text = _doc_text()
    assert "config/pricing_config.yaml" in text
    assert "api_base_url" in text
    assert "허용 host" in text
    assert "allowed host set" in text


def test_docs_link_github_and_hf_space_reciprocally():
    text = _doc_text()
    github_url = "https://github.com/woooya129-ai/k-fashion-persona"
    hf_space_url = "https://huggingface.co/spaces/w00ya/k-fashion-persona"
    live_app_url = "https://w00ya-k-fashion-persona.hf.space"

    assert text.count(github_url) >= 2
    assert text.count(hf_space_url) >= 2
    assert text.count(live_app_url) >= 2


def test_docs_state_public_space_requires_user_provider_key():
    text = _doc_text()

    assert "KFPS_REQUIRE_USER_PROVIDER_KEY=1" in text
    assert "운영자 공용 LLM provider API key를 사용하지 않으며" in text
    assert "does not use shared owner LLM provider API keys" in text


def test_hf_space_frontmatter_is_configured():
    readme = _read("README.md")
    assert readme.startswith("---\n")
    frontmatter = yaml.safe_load(readme.split("---", 2)[1])

    assert frontmatter["title"] == "K-Fashion Persona"
    assert frontmatter["sdk"] == "docker"
    assert frontmatter["app_port"] == 7860
    assert "app_file" not in frontmatter
    assert "sdk_version" not in frontmatter
    assert frontmatter["colorFrom"] in {
        "red",
        "yellow",
        "green",
        "blue",
        "indigo",
        "purple",
        "pink",
        "gray",
    }
    assert frontmatter["colorTo"] in {
        "red",
        "yellow",
        "green",
        "blue",
        "indigo",
        "purple",
        "pink",
        "gray",
    }


def test_hf_space_dockerfile_runs_streamlit_on_declared_port():
    dockerfile = _read("Dockerfile")

    assert "FROM python:3.11-slim" in dockerfile
    assert "pip install -r requirements.txt" in dockerfile
    assert '"streamlit", "run", "src/app.py"' in dockerfile
    assert '"--server.address=0.0.0.0"' in dockerfile
    assert '"--server.port=7860"' in dockerfile
    assert "EXPOSE 7860" in dockerfile


def test_project_version_matches_pyproject():
    pyproject = tomllib.loads(_read("pyproject.toml"))
    readme = _read("README.md")
    readme_en = _read("docs/README-ENG.md")
    version = pyproject["project"]["version"]

    assert f"version-{version}" in readme
    assert f"version-{version}" in readme_en
