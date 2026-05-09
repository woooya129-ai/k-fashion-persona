# Changelog

## 0.5.0 - 2026-05-09

- Split the large Streamlit entry point into `src/ui/`, `src/orchestrator/`, and `src/app_config.py`.
- Kept `src.app` compatibility wrappers for existing tests and monkeypatch paths.
- Updated the AppTest fixture for the `_load_and_sample(..., hf_token=...)` signature.
- Moved logging setup from import time to app startup.
- Updated package and UI release labels to `0.5.0`.

## 0.4.1 - 2026-05-09

- Hardened KOSIS URL validation.
- Removed Hugging Face token injection into process environment.
- Added structured result-payload validation before report aggregation.
