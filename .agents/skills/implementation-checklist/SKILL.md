---
name: implementation-checklist
description: Use before and during code changes in this repo to keep implementation scoped, tested, and release-safe.
---

# Implementation Checklist

## Before Editing

- Check `git status --short`.
- Inspect nearby code and tests before changing files.
- Identify whether the change is backend, frontend, data/API, docs, or release metadata.
- Avoid touching unrelated files.

## During Editing

- Prefer existing helpers and patterns.
- Use structured parsing instead of ad hoc string handling when reasonable.
- Preserve user edits and untracked local reference folders.
- Keep comments short and only where they reduce cognitive load.

## After Editing

Run targeted tests first, then release gates when the change affects shared behavior:

```powershell
python -m compileall -q src tests
ruff check .
ruff format src tests --check
python -m pytest -q --basetemp .pytest_tmp_codex_verify -p no:cacheprovider
```

For release work also run:

```powershell
bandit -q -c pyproject.toml -r src
pip-audit --skip-editable
```
