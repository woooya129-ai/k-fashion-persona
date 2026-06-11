# fable 5-ui-comment — UI 재구성 추천안 (v0.8.0 / Streamlit 기준)

> 작성일: 2026-06-12 / 대상: k-fashion-persona 작업자
> 짝 문서: [fable 5-comment.md](fable%205-comment.md) — 입력 간소화·텍스트 대처법.
> 이 문서는 그 제안들을 **현재 Streamlit 단일 페이지 + 사이드바 구조** 위에
> 어떻게 배치할지를 다룬다. 프레임워크 교체 없이 기존 컴포넌트 재배치가 원칙.

---

## 1. 현재 화면 흐름 (main(), app.py:684-803)

```
[탑바: 언어/테마]
[히어로 헤더]
[빠른 가이드 4카드]            ← 매 세션 큰 면적 차지
[시크릿 상태 expander]
─────────────────────────────
사이드바: 실행 모드 → Advanced expander(데이터셋/패널/temp)
         → 모델 선택 → API key → HF token → KOSIS    ← 설정 6종 혼재
─────────────────────────────
[섹션밴드: 프로젝트]
[컨셉 입력 4구획 × 3열 그리드]  ← ENTER 카드가 마지막 행 3번째 열에 위치
[실행 안내 패널]
[비용 확인 체크박스]            ← 게이트(체크박스)는 아래,
[주입 경고 체크박스(조건부)]       버튼(ENTER)은 위 — 공간 분리
[잡 패널 fragment: 1초 폴링 → 진행/리포트/CSV]
[상세 실행 컨텍스트 expander]
[푸터]
```

**UI 관점의 핵심 문제 4가지**

1. **실행 게이트 분산**: ENTER 버튼은 컨셉 그리드 안(rendering.py:1255-1258), 비용 확인 체크박스는 그 아래(app.py:728), 비활성 사유 안내는 또 그 아래(app.py:758-761). 버튼이 왜 안 눌리는지 한눈에 안 보임.
2. **설정 동선 단절**: 필수 준비(모델/key)가 사이드바에 있어 본문만 보는 신규 사용자는 막힌 이유를 못 찾음. 사이드바엔 KOSIS·HF token 등 선택 항목까지 섞여 있어 필수/선택 구분이 없음.
3. **첫 화면 정보 과잉**: 가이드 4카드 + 시크릿 상태 + 섹션밴드가 입력 영역보다 먼저 나옴. 정작 "여기부터 채우세요"라는 시작점이 없음.
4. **결과 진입 거리**: 리포트가 길어 요약을 보려면 스크롤. (자동 스크롤 anchor는 이미 있음 — 잘 된 부분)

---

## 2. 재구성 추천안 — 3-스텝 수직 구조

기존 `render_section_band`(rendering.py:830)를 그대로 스텝 헤더로 활용한다. 멀티페이지 전환 불필요.

```
[탑바]
[히어로 헤더(축소)]
[가이드: 첫 실행 전엔 4카드, 실행 1회 후엔 한 줄 expander]

══ STEP 1 · 준비 ════════════════════════
  [준비 체크리스트 칩]  모델 ✓ · API key ✗ · 데이터셋 ✓
  (미충족 칩 클릭 → 사이드바 해당 항목 안내)

══ STEP 2 · 컨셉 입력 ═══════════════════
  [탭: 빠른 입력 | 직접 입력 | 예시 불러오기]
   ├ 빠른 입력: 큰 텍스트박스 1개 + "필드로 분해" 버튼  (짝 문서 P1)
   ├ 직접 입력: 필수 3필드 상단 + 나머지 expander       (짝 문서 P3)
   └ 이미지 보조 토글은 두 탭 모두에서 접근 가능 (기본 OFF 유지)

══ STEP 3 · 실행 ════════════════════════
  [전폭 실행 카드: 예상 비용·시간·인원 요약 + ENTER]
  클릭 → st.dialog 로 비용 최종 확인 → 시작
  (비활성 시: 미충족 조건 목록을 카드 안에 직접 표시)

══ 결과 ═════════════════════════════════
  [요약 카드: 긍정률 / 최대 리스크 / 다음 액션]
  [탭: 요약 | 전체 리포트 | 원문(MD) | CSV]
─────────────────────────────────────────
사이드바 (슬림화): 실행 모드 · 모델 · API key 만
  └ "고급 설정" expander: 데이터셋/패널 필터/temp/HF token/KOSIS
```

### R1. 실행 게이트 통합 — 전폭 실행 카드 + `st.dialog`

가장 효과 큰 변경. 흩어진 ENTER/체크박스/안내를 한 곳에 모은다.

- ENTER 카드를 컨셉 그리드 3번째 열에서 빼서 **STEP 3 전폭 카드**로 이동
- 비용 확인 체크박스(app.py:728) 제거 → ENTER 클릭 시 `@st.dialog`로 비용·시간·인원을 보여주고 "확인 후 시작" 버튼. 주입 경고도 같은 다이얼로그 안에 조건부 표시 → 체크박스 2개가 모달 1개로 통합
- 비활성 상태일 때: `run_button_disabled`(app.py:746-757)의 합성 불리언을 **이름 있는 체크 목록**으로 분해해 카드 안에 직접 렌더

```python
checks = [
    (ui_text(lang, "check_api_key"), bool(api_key)),
    (ui_text(lang, "check_category"), bool(concept["category"])),
    (ui_text(lang, "check_description"), has_user_concept_input),
    (ui_text(lang, "check_dataset"), local_ready),
]
# 미충족 항목만 ✗ 로 카드에 표시 → "왜 안 되는지" 즉답
```

### R2. STEP 1 준비 체크리스트 칩 (본문 ↔ 사이드바 연결)

- 본문 최상단에 모델/key/데이터셋 상태 칩 행 추가 — `render_secrets_status`(rendering.py:989)의 카드 그리드 CSS(`kfps-secret-status-card`)를 재사용하면 신규 CSS 거의 불필요
- 기존 시크릿 상태 expander는 이 칩 행의 상세 보기로 격하 (혹은 흡수)
- 칩이 ✗ 면 "사이드바에서 입력하세요" 캡션 — Streamlit에서 사이드바 자동 오픈은 불가하므로 텍스트 안내로 충분

### R3. 사이드바 슬림화 — 필수/선택 분리

`render_simple_setup`(rendering.py:1523) 내부 재배치만으로 가능:

- 상단 유지: 실행 모드 segmented control + 모델 selectbox + API key
- 하단 "고급 설정" expander 1개로 통합: 기존 Advanced(데이터셋/샘플/temp) + HF token + KOSIS 입력(`render_kosis_inputs`) 전부 이동
- KOSIS는 스냅샷 fallback이 이미 있으므로(README) 미입력 동작에 영향 없음 — 선택 항목임을 구조로 보여주는 것

### R4. 컨셉 입력 영역 — `st.tabs` 3탭

`render_concept_inputs`(rendering.py:1112)를 탭 컨테이너로 감싼다:

- **빠른 입력 탭**: 텍스트박스 1개 + "필드로 분해" 버튼 (짝 문서 P1의 `concept_parser`). 분해 결과는 직접 입력 탭의 위젯에 채워지고 자동으로 그 탭 안내 표시
- **직접 입력 탭**: 현재 그리드 유지하되 필수 3필드(카테고리/가격/설명)를 첫 행으로, 핏/소재/컬러/시즌/디테일/톤/타깃은 "선택 입력" expander로
- **예시 탭**: 프리셋 2~3개 카드 + "이 예시로 채우기" 버튼 (짝 문서 P4)
- 주의: 탭 간 위젯 키 충돌 방지 — 같은 `kfps_*` 키를 두 탭에서 만들면 `DuplicateWidgetID`. 위젯은 직접 입력 탭에만 두고, 빠른 입력/예시 탭은 session_state 주입 + `st.rerun()`만 수행

### R5. 가이드 카드 — 첫 성공 후 자동 축소

- `st.session_state["kfps_has_completed_run"]` 플래그 (잡 패널에서 TERMINAL 상태 도달 시 set)
- 플래그가 있으면 `render_quick_guide`(rendering.py:902) 대신 한 줄 expander("사용 방법 다시 보기")로 렌더
- 신규 사용자는 가이드를 보고, 재방문자는 입력이 첫 화면이 됨

### R6. 결과 영역 — 요약 우선 + 탭 통합

`_render_job_panel_impl`(app.py:520) 수정:

- 진행 중: 현재 metric 5개 행 → `st.status` 컨테이너 1개로 교체 (status/total/cached를 라벨 한 줄로). fragment 1초 폴링 구조는 유지
- 완료 후 최상단에 요약 카드: 긍정률 % / 최대 리스크 카테고리 1개 / 수정 제안 1순위 — 전부 `build_run_report` 결과에 이미 있는 값이라 추출만 하면 됨
- 현재 2탭(렌더/원문) → 4탭: **요약 | 전체 리포트 | 원문 | 다운로드**(MD+CSV 버튼 묶음). CSV 다운로드가 페이지 최하단에 떨어져 있는 문제(app.py:641) 해결

---

## 3. 구현 팁

### 3-1. 손대는 파일이 적은 순서

| 순서 | 작업 | 파일 | 규모 |
|---|---|---|---|
| 1 | R5 가이드 자동 축소 | rendering.py(902) + 잡 패널 플래그 1줄 | ~30분 |
| 2 | R1 체크 목록 분해·표시 | app.py(746-757) → 이름 있는 checks 리스트 | 반나절 |
| 3 | R3 사이드바 재배치 | rendering.py(1523) 내부 이동만 | 반나절 |
| 4 | R6 결과 요약 카드+4탭 | app.py(520-649) | 1일 |
| 5 | R1 `st.dialog` 비용 확인 | app.py(728~) + 신규 dialog 함수 | 1일 |
| 6 | R4 입력 3탭 | rendering.py(1112) + concept_parser 연동 | P1 작업과 함께 |
| 7 | R2 준비 칩 | rendering.py 신규 함수 + 기존 CSS 재사용 | 반나절 |

### 3-2. `st.dialog` 패턴 (R1)

```python
@st.dialog("실행 전 확인")
def confirm_run_dialog(cost_state, injection_hits, lang):
    st.metric("예상 비용", _format_cost_range(cost_state["cost_estimate"]))
    st.metric("패널 인원", f"{cost_state['new_call_count']}명")
    if injection_hits:
        st.warning(ui_text(lang, "injection_warning"))
    if st.button(ui_text(lang, "run_button"), type="primary"):
        st.session_state["kfps_enter_requested"] = True
        st.rerun()
```

기존 `kfps_enter_requested` 플래그 경로(app.py:765)를 그대로 타므로 `start_screening` 호출부는 무수정. 체크박스 키(`kfps_cost_confirm`, `kfps_injection_confirm`)를 참조하는 테스트가 있는지 `grep -r kfps_cost_confirm tests/` 먼저 확인.

### 3-3. AppTest 호환 주의

- 잡 패널은 `KFPS_APPTEST_SYNC_JOB_PANEL` env로 fragment 폴링을 우회한다(app.py:798). 결과 영역을 고칠 때 `_render_job_panel_impl` 동기 경로가 깨지지 않게 유지
- `st.dialog`는 AppTest에서 직접 트리거가 까다로움 — dialog 내부 로직을 일반 함수로 분리하고 dialog는 얇은 래퍼로 (이 프로젝트의 "thin orchestration layer" 원칙과 동일)
- `_COMPAT_UI_EXPORTS`(app.py:167)에 묶인 함수 시그니처는 외부 호환 표면이므로 이름 변경 대신 신규 함수 추가 방식 권장

### 3-4. CSS / 디자인 시스템

- 신규 컴포넌트(체크 목록, 요약 카드, 준비 칩)는 `static_css.py`의 기존 클래스(`kfps-secret-status-*`, `kfps-run-panel`, `kfps-flow-card`) 변형으로 — 새 디자인 언어를 만들지 말 것
- 다크모드는 `apply_design_system(dark)` 경유라 하드코딩 색상 금지, 기존 CSS 변수 사용

### 3-5. 점진 적용 전략

각 R 항목은 독립적이라 한 번에 한 PR씩 가능. 추천 분할: ① R5+R1체크목록 (저위험 UX 즉효) → ② R3+R2 (설정 동선) → ③ R6 (결과) → ④ R1 dialog → ⑤ R4 (짝 문서 P1과 동시).

---

*본 문서는 v0.8.0 코드 리딩 기반이며, Streamlit 단일 페이지 구조·fragment 폴링·AppTest 테스트 체계를 유지하는 범위 내의 재배치안이다. 입력 간소화 로직 자체는 [fable 5-comment.md](fable%205-comment.md) 참고.*
