import tomllib
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.no_network

DOC_PATHS = (
    Path("README.md"),
    Path("README-ENG.md"),
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
    readme_en = _read("README-ENG.md")
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


def test_hf_space_frontmatter_is_configured():
    readme = _read("README.md")
    assert readme.startswith("---\n")
    frontmatter = yaml.safe_load(readme.split("---", 2)[1])

    assert frontmatter["title"] == "K-Fashion Persona"
    assert frontmatter["sdk"] == "streamlit"
    assert frontmatter["app_file"] == "src/app.py"
    assert frontmatter["python_version"] == "3.11"
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


def test_requirements_matches_pyproject_runtime_dependencies():
    project = tomllib.loads(_read("pyproject.toml"))
    requirements = {
        line.strip()
        for line in _read("requirements.txt").splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert requirements == set(project["project"]["dependencies"])


def test_local_runtime_dirs_are_gitignored():
    gitignore = _read(".gitignore")
    for pattern in (".obsidian/", ".venv/", ".pytest_cache/", "sandbox/"):
        assert pattern in gitignore
