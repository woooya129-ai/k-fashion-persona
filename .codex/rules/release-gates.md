# Release Gates

릴리스, 태그, GitHub push, Hugging Face Space sync 전에는 아래를 확인한다.

## Required Checks

```powershell
python -m compileall -q src tests
ruff check .
ruff format src tests --check
bandit -q -c pyproject.toml -r src
pip-audit --skip-editable
python -m pytest -q --basetemp .pytest_tmp_codex_verify -p no:cacheprovider
```

## Metadata Sync

- `pyproject.toml`
- `uv.lock`
- `CITATION.cff`
- `docs/docs.html`
- Hugging Face README frontmatter

## Known Regression Hotspots

- KOSIS/KOSTAT unit and currency formatting.
- HF dataset sampling seed reproducibility.
- `matched_count_before_sample` semantics.
- Agent Pack manifest count, missing persona IDs, bad JSON/non-JSON files.
- Streamlit slider and direct number input session state sync.
- Model pricing and model alias names from official OpenAI docs.
