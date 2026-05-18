# Changelog

## v0.7.0 - 2026-05-18

- Added `concept_eval_ko_v0_4` and moved the default prompt template to the new version so cache keys are separated from v0.3.
- Added input-grounding prompt rules for design details, price, product audience, occasion, and season.
- Added structured design-detail inputs, style-tone presets, and peer-brand price-position metadata.
- Added age lower/upper controls with direct numeric inputs for finer panel targeting.
- Added one-time adjacent age assist when an age filter yields too few personas, with the assist ratio shown in reports.
- Added deterministic validation flags and a three-line report summary on `AggregateReport` without changing `EvaluationResult`.
- Added a shared `src/public_data/` foundation for future government/public API connectors.
- Added KOSIS API call status metadata in reports while preserving snapshot fallback.
- Updated project version labels to `0.7.0`.

## v0.6.1 - 2026-05-15

- HF 스트리밍 샘플링에서 제품 성별 필터가 켜져 있으면 100행 제한으로 먼저 자르지 않고, 요청한 패널 수를 채울 수 있도록 필터 통과 행을 계속 읽음.
- 여성/남성 제품 선택 시 이성 패널이 섞여 샘플 수가 부족해지는 문제를 수정.
- 프로젝트 버전 표기를 `v0.6.1`로 통일.

## v0.6.0 - 2026-05-15

- 컨셉 입력 아래 제품 성별 선택을 `여성 / 남성 / 유니섹스` 3버튼으로 배치.
- 제품 성별 버튼을 내부 페르소나 필터 `F / M / UNI` 흐름에 연결.
- 실행 시작 시 `작동 중이에요` 안내를 표시하고, 작업 시작 후 안내가 사라지도록 정리.
- 진행 상태 도움말에 `success`, `failed`, `cached` 기준을 추가.
- 리포트 기본 탭을 `미리보기`로 변경.
- 한국어 안내 문구를 존댓말 `-요` 톤으로 정리.
- 프로젝트 버전 표기를 `v0.6.0`으로 통일.

## 0.5.3 - 2026-05-10 (Attribution and rights positioning)

- Added `CITATION.cff` to make project attribution explicit.
- Added `docs/legal/METHODOLOGY_AND_RIGHTS.md` to document the pre-screening workflow,
  attribution expectations, commercial adoption boundary, and IP positioning.
- Clarified README, commercial-license, and NOTICE references for citation,
  methodology, branding, and commercial adoption.
- Updated release labels to `0.5.3`.

## 0.5.2 - 2026-05-09 (CI validation)

- Verified that `actions/checkout@v6` and `actions/setup-python@v6` are published GitHub Marketplace versions.
- Kept `pip install -e . --group dev`; current pip documents the `--group` install option.
- Added `pip-audit --skip-editable` to CI after pip upgrade and local validation.
- Updated release labels to `0.5.2`.

## 0.5.1 - 2026-05-09 (License policy)

### License

- Project license remains GNU AGPL-3.0-only (unchanged for OSS use).
- Added: Commercial license option for closed-source/SaaS adoption.
- See `docs/legal/LICENSE-COMMERCIAL.md` and contact woooya129@gmail.com.
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
