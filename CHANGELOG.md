# Changelog

## 0.5.2 - 2026-05-09 (CI validation)

- Verified that `actions/checkout@v6` and `actions/setup-python@v6` are published GitHub Marketplace versions.
- Kept `pip install -e . --group dev`; current pip documents the `--group` install option.
- Added `pip-audit --skip-editable` to CI after pip upgrade and local validation.
- Updated release labels to `0.5.2`.

## 0.5.1 - 2026-05-09 (License policy)

### License

- Project license remains GNU AGPL-3.0-only (unchanged for OSS use).
- Added: Commercial license option for closed-source/SaaS adoption.
- See `LICENSE-COMMERCIAL.md` and contact woooya129@gmail.com.
- Pre-0.5.1 versions are AGPL-3.0-only and remain valid under that license
  for those who already received them.

### Contributing

- All future contributions require DCO signoff (`git commit -s`).
- By contributing, you acknowledge the project may be redistributed under
  additional written license terms by the copyright holder. Unless a separate
  contributor agreement says otherwise, public repository contributions are
  accepted under AGPL-3.0-only.

### CI

- Added GitHub Actions CI for linting, formatting, security scan, and tests.

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
