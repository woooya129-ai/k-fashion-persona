# fable 5-handoff — 작업 인수인계 (다음 작업자용)

> 작성일: 2026-06-12 / 작성: 총괄(오케스트레이터)
> 상태: Phase 1(병렬 빌드) + Phase 2(백엔드↔UI 연결) **완료**. Phase 3(마감) 일부 남음.
> 관련 문서: [comment](fable%205-comment.md)(입력 간소화 P1~P7) · [ui-comment](fable%205-ui-comment.md)(UI 재구성 R1~R6) · [workplan](fable%205-workplan.md)(분담·계약)

---

## 1. 지금 어디까지 됐나 (한눈에)

- **브랜치**: `integration/fable5` — **origin에 push 완료**, 로컬이 `origin/integration/fable5` 추적 중. main 기준 머지 커밋 4개 + Phase 2 커밋 1개 + 문서 커밋.
- **PR**: 아직 안 열림. 생성 링크 → `https://github.com/woooya129-ai/k-fashion-persona/pull/new/integration/fable5` (또는 `gh pr create`).
- **GitHub 인증**: `gh` CLI(`~/.local/bin/gh`, v2.94.0)로 `woooya129-ai` 로그인 완료(device flow, 토큰 keyring 저장, `repo` 권한). `gh auth setup-git` 적용돼 이 머신에선 추가 push/PR이 프롬프트 없이 동작.
- **테스트**: `787 passed, 1 failed`. 신규 +12건 전부 통과, **회귀 0건**.
  - 유일한 실패는 **기존부터 있던** `tests/test_docs_text.py::test_user_docs_and_default_prompt_avoid_forbidden_public_claim_phrases` — README의 "구매율 예측**에는 쓰지 않습니다**"(부정문)를 단순 부분 문자열로 걸러낸 오탐. 우리 작업과 무관(§5 참고).
- **검증 명령**: `uv run pytest --tb=no -p no:cacheprovider -o addopts=""`
  - 워크트리 샌드박스엔 uv가 없었어서 통합 테스트는 **메인 리포(.venv)** 에서 돌렸음. `uv sync --all-extras --dev` 선행 필요.

---

## 2. 완료된 작업 (P/R 항목별)

| 항목 | 내용 | 핵심 파일 |
|---|---|---|
| **P1** | 자유 텍스트 → 11필드 자동 분해. 빠른 입력 탭에서 세션 모델로 실제 LLM 호출 → 위젯 자동 채움 | `src/concept_parser.py`, `src/ui/rendering.py` |
| **P2** | 핏/시즌/착용상황 프리셋(칩) 전환 | `src/app_config.py`(FIT/SEASON/OCCASION_PRESETS), rendering.py |
| **P3** | 직접 입력 탭: 필수 3필드(카테고리/가격/설명) 상단 + 나머지 "선택 입력" expander | rendering.py `render_concept_inputs` |
| **P4** | 예시 프리셋 3종(출근 셔츠/주말 니트/운동 탑) + "이 예시로 채우기" | `CONCEPT_EXAMPLE_PRESETS`(app_config) |
| **P6** | 프리뷰(5명) 실행 모드 | `RUN_MODE_PRESETS["preview"]`(app_config) |
| **P7** | 이미지 보조: Anthropic/Google analyzer 추가 + **세션 key 재사용**(env 불필요) | `src/image_assist.py` |
| **R1(부분)** | 게이트 합성 불리언 → 이름 있는 체크리스트, 미충족 ✗ 표시 | `src/app.py` main() |
| **R2** | 준비 상태 칩(모델/key/데이터셋) | rendering.py `render_readiness_chips` |
| **R3** | 사이드바 슬림화: 필수 상단 + "고급 설정" expander 통합 | rendering.py `render_simple_setup` |
| **R5** | 첫 실행 후 가이드 4카드 자동 축소 | rendering.py `render_quick_guide` |
| **R6+P5** | 결과 요약 카드(긍정률/최대 리스크/1순위 제안) + 4탭(요약/전체/원문/다운로드) + 진행 `st.status` | app.py `_render_job_panel_impl` |

---

## 3. 남은 작업 (다음 작업자가 할 것)

우선순위 순:

### 3-1. R1 `st.dialog` 비용 확인 전환 (보류했던 항목)
현재는 비용 확인이 **체크박스**(`kfps_cost_confirm`)이고 게이트 체크리스트에 흡수된 상태. 계획대로 모달로 올리는 작업이 남음.
- 위치: `src/app.py` main(), 게이트 체크리스트 직후 ENTER 버튼 흐름.
- 팁: `@st.dialog` 래퍼 안에서 비용/시간/인원 + 주입 경고를 보여주고, 확인 버튼이 기존 `st.session_state["kfps_enter_requested"] = True` 플래그를 세팅 → `start_screening` 호출부 무수정.
- **AppTest 주의**: dialog 내부 로직을 일반 함수로 분리하고 dialog는 얇은 래퍼로. `tests/test_app.py`가 `kfps_cost_confirm`를 참조하면 같이 수정.

### 3-2. 버전 범프 v0.8.0 → v0.9.0
`test_docs_text.py::test_release_version_metadata_is_aligned`가 **여러 파일의 버전 일치를 강제**함. 한 곳만 바꾸면 테스트 깨짐. 동시에 고칠 곳:
- `pyproject.toml` `[project].version`
- `uv.lock` (k-fashion-persona 패키지 version) — `uv lock` 재생성
- `src/app_config.py` `APP_VERSION`
- `CITATION.cff` `version:`
- `docs/CHANGELOG.md`, `docs/docs.html`, `src/ui/copy.py` (`v0.9.0` 문자열)
- README 배지 `version-0.9.0`, README 본문 "현재 버전" 섹션

### 3-3. README / docs 사용법 갱신
3탭 입력·예시·프리뷰·요약 카드 등 새 UX 반영. `docs/README-ENG.md`도 동일하게.

### 3-4. (선택) 기존 오탐 테스트 정리
§5의 `test_docs_text` 오탐. README 부정문은 정당하므로, 테스트의 blocked 매칭을 문맥 인식형으로 고치거나 해당 부정 문장을 예외 처리. **README/test 의미를 바꾸는 변경이라 단독 판단 말고 확인 후 진행 권장.**

---

## 4. 다음 작업자가 알아야 할 핵심 계약 (건드리면 깨지는 것)

### 4-1. 자동 채움 상태키 화이트리스트 (이 외 주입 금지)
`src/app_config.py` `CONCEPT_AUTOFILL_STATE_KEYS`:
```
kfps_product_category · kfps_fit · kfps_material · kfps_color ·
kfps_season · kfps_occasion · kfps_style_tone ·
kfps_target_hypothesis · kfps_concept_description
```
`design_details`는 체크박스 기반이라 **의도적으로 자동 채움 제외**.

### 4-2. parser 인터페이스 (A 제공)
```python
# src/concept_parser.py
parse_concept_text(raw_text, *, llm_call: Callable[[str], str]) -> ConceptDraft
#   ConceptDraft.fields: dict (필드명 키: category/fit/.../description)
#   ConceptDraft.fallback_description_only: bool (JSON 파싱 실패 시 True)
build_concept_llm_call(provider, model, api_key) -> Callable[[str], str]
```
UI 연결 글루: rendering.py `_PARSER_FIELD_TO_STATE_KEY`(필드명→kfps_*), `_fields_to_state_keys()`, `_run_concept_parser()`.

### 4-3. 세션 모델 전달 통로
`src/app.py` main()이 `st.session_state["kfps_active_model"] = {provider, model_name, api_key, supports_vision}`를 채움. 빠른 입력 parser와 이미지 analyzer가 이걸 읽음. **render_concept_inputs 시그니처는 안 바꿈** (세션으로 전달).

### 4-4. 깨면 안 되는 안전 불변식
이미지 바이트/base64/원문이 **평가 payload·리포트·로그·스냅샷에 절대 안 들어감**. 모든 자동화는 "수정 가능한 위젯에 draft 주입"까지. 평가 루프엔 사용자가 확인한 텍스트만. 테스트: `tests/test_image_assist.py`, `tests/test_concept_parser.py`.

### 4-5. 문구 키
새 ui_text 키는 **반드시 KR+EN 둘 다**(`src/ui/copy.py`). 현재 308/308 일치. 깨지면 `ui_text(EN, ...)`가 KeyError. 검증:
```bash
uv run python -c "from src.ui.copy import UI_COPY; k,e=set(UI_COPY['KR']),set(UI_COPY['EN']); print(k^e or 'OK')"
```

### 4-6. AppTest 동기 경로
잡 패널은 `KFPS_APPTEST_SYNC_JOB_PANEL` env로 fragment 폴링 우회(app.py 하단). 결과 영역 수정 시 `_render_job_panel_impl` 동기 경로 유지.

---

## 5. 기존 테스트 실패 1건 (우리 책임 아님)
`test_docs_text.py:167` — blocked 구문에 `"구매율 예측"`이 있는데 README가 "…구매율 예측**에는 쓰지 않습니다**"라는 부정문에서 이 부분 문자열을 포함. **clone 직후 main에서도 실패**(베이스라인 775 passed / 1 failed). 통합으로 새로 생긴 실패 아님. 처리 방향은 §3-4.

---

## 6. 머지 히스토리 / 정리 상태
```
integration/fable5
  1e247e8 Phase 2: wire concept_parser + session image analyzer into UI
  da885e2 Merge stream A (parser + multi-provider image + vision flags)
  709c035 Merge stream B (3-tab input + presets + examples)
  89a4674 Merge stream C (gate checklist + sidebar slim + chips + preview)
  ed6ab88 Merge stream D (summary card + 4-tab + guide collapse)
```
- 작업용 worktree(kfp-a/b/c/d)는 머지 후 제거 완료. feature 브랜치(`feat/*`)는 로컬에 남아 있음(필요시 `git branch -d`). origin에는 `integration/fable5`만 올라감.
- 이어받기(같은 머신): `git checkout integration/fable5 && git pull && uv sync --all-extras --dev && uv run streamlit run src/app.py`
- 이어받기(다른 머신/새 클론): `git clone ... && git checkout integration/fable5` 후, push/PR 하려면 `gh auth login`(device flow) 1회 필요 — 현재 토큰은 이 머신 keyring에만 있음.
- PR 생성 예시: `gh pr create --base main --head integration/fable5 --title "fable5: 입력 간소화 + UI 재구성" --body-file "fable 5-handoff.md"`

---

*다음 작업자: §3을 위에서부터. 막히면 §4 계약부터 확인. 안전 불변식(§4-4)은 어떤 경우에도 우선.*
