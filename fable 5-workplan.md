# fable 5-workplan — 병렬 작업 분담·진행 플랜

> 작성일: 2026-06-12 / 작성: 총괄(오케스트레이터)
> 입력 문서: [fable 5-comment.md](fable%205-comment.md) (P1~P7 입력 간소화),
> [fable 5-ui-comment.md](fable%205-ui-comment.md) (R1~R6 UI 재구성)
> 목표: P/R 항목 13개를 충돌 없이 병렬 진행하고, 2회 통합과 최종 검수로 마무리.

---

## 1. 분담 설계의 근거 — 충돌 지점부터

병렬화의 적은 기능 난이도가 아니라 **같은 파일을 동시에 만지는 것**이다. 이 프로젝트의 공유 핫스팟:

| 핫스팟 | 위치 | 겹치는 작업 |
|---|---|---|
| `rendering.py` (2,458줄) | 입력(1112-1295) / 사이드바(1523-1708) / 가이드(902) 영역 혼재 | B·C·D 전원 |
| `app.py main()` (684-803) | 게이트 로직 + 잡 패널 + 흐름 | C·D |
| `copy.py` ui_text 키 | 전 스트림이 신규 문구 추가 | 전원 |
| `session_state` 키 | 자동 채움·플래그·dialog 전부 사용 | A·B·C |

→ 해법: **파일이 아니라 "라인 영역 + 키 네임스페이스" 단위로 소유권을 나눈다** (§4 계약 참조).

---

## 2. 역할 분담 (5개 스트림 + 검수 2단)

### 총괄 — 오케스트레이터 (본 문서 작성자)
- §4 인터페이스 계약 동결·변경 승인 (계약 변경은 총괄 승인 없이 금지)
- 머지 순서 통제, 스트림 간 충돌 중재, 일일 싱크 주재
- 각 Phase 게이트에서 진행/보류 판단

### 스트림 A — LLM 통합 엔지니어 (백엔드, UI 미접촉)
| 담당 | 범위 |
|---|---|
| **P1 로직** | 신규 `src/concept_parser.py`: 텍스트 → 11필드 JSON 분해. 프롬프트, json 파싱(코드펜스 제거 재시도), description-only fallback |
| **P7 전체** | `src/image_assist.py`: 세션 key 재사용 팩토리 `image_analyzer_for_session()`, Anthropic/Google analyzer 추가, JSON 분해 프롬프트 적용, `pricing_config.yaml`에 `supports_vision` 플래그 |
| 산출물 | 순수 함수 모듈 + 단위 테스트. **Streamlit 코드 한 줄도 만지지 않음** — UI 연결은 B가 함 |

### 스트림 B — 입력 UI 엔지니어 (Streamlit)
| 담당 | 범위 |
|---|---|
| **R4** | `render_concept_inputs`(rendering.py:1112-1295)를 3탭(빠른 입력/직접 입력/예시)으로. 위젯은 직접 입력 탭에만, 나머지 탭은 state 주입+`st.rerun()` |
| **P3** | 직접 입력 탭: 필수 3필드 상단 + 나머지 "선택 입력" expander |
| **P2** | 핏/시즌/착용 상황 칩·프리셋 전환 (옵션 상수는 `app_config.py`에) |
| **P4** | 예시 프리셋 2~3종 + "이 예시로 채우기" |
| **P1 UI** | 빠른 입력 탭 ↔ A의 concept_parser 연결 (Phase 1에서는 mock parser로 개발) |
| 소유 영역 | rendering.py **1050-1295** + 신규 입력 컴포넌트 함수 |

### 스트림 C — 실행 흐름·설정 UI 엔지니어 (Streamlit)
| 담당 | 범위 |
|---|---|
| **R1** | `run_button_disabled` 합성 불리언(app.py:746-757) → 이름 있는 체크 목록 분해·표시 → 이후 `st.dialog` 비용 확인 (체크박스 2개 제거) |
| **R3** | `render_simple_setup`(rendering.py:1523-1708) 슬림화: 필수 상단 / "고급 설정" expander 통합 |
| **R2** | 준비 체크리스트 칩 (기존 `kfps-secret-status-*` CSS 재사용) |
| **P6** | `RUN_MODE_PRESETS`에 `preview`(5명) 프리셋 추가 |
| 소유 영역 | app.py **684-803** (잡 패널 호출부 제외) + rendering.py **1523-1708** |

### 스트림 D — 결과·리포트 UI 엔지니어 (Streamlit)
| 담당 | 범위 |
|---|---|
| **R6 + P5** | `_render_job_panel_impl`(app.py:520-655): 요약 카드(긍정률/최대 리스크/다음 액션) 우선 + 4탭(요약/전체/원문/다운로드), 진행 표시 `st.status` 전환. `build_run_report` 출력 구조는 무수정 |
| **R5** | 가이드 자동 축소: `kfps_has_completed_run` 플래그 set(잡 패널 TERMINAL 도달 시) + `render_quick_guide`(rendering.py:902) 분기 |
| 소유 영역 | app.py **520-682** + rendering.py **830-1048** (가이드·섹션밴드 영역) |

### 스트림 E — QA/테스트 엔지니어 (전 Phase 상주)
- 신규 모듈(A) 단위 테스트 리뷰, JSON 파싱 실패 fallback 경로 테스트 필수 확인
- AppTest 회귀: `KFPS_APPTEST_SYNC_JOB_PANEL` 동기 경로, 제거되는 체크박스 키(`kfps_cost_confirm` 등) 참조 테스트 사전 grep·정리
- **안전 불변식 수호**: 이미지 바이트/원문 텍스트가 평가 payload·리포트·로그에 새지 않는지 — 기존 raw-image 차단 테스트 + 신규 parser 경로용 동일 테스트 추가
- 각 PR에 테스트 체크리스트 첨부, 통과 전 머지 불가

### 최종 검수자 — 시니어 리뷰어 (Phase 3 게이트)
머지된 통합 브랜치 전체를 1회 검수. 체크 항목:
1. 안전 경계: 모든 자동화가 "draft 제안 → 사용자 확인 텍스트만 평가 루프" 패턴 준수
2. `_COMPAT_UI_EXPORTS`(app.py:167) 시그니처 보존 — 변경 대신 신규 함수 추가됐는지
3. 디자인 시스템: 신규 CSS가 기존 클래스 변형인지, 하드코딩 색상 없는지(다크모드)
4. SPDX 헤더(AGPL-3.0-only), 신규 ui_text 키의 KR/EN 양쪽 존재
5. README·docs 갱신 여부, 사용자 시나리오 E2E 1회 실행("예시 불러오기 → 5명 프리뷰 → 요약 확인")

---

## 3. 진행 순서 — 3 Phase

```
Phase 0 (총괄, 0.5일)
  └ 인터페이스 계약 동결(§4) · 브랜치 생성 · 키 레지스트리 배포

Phase 1 — 전면 병렬 (약 1주)         ※ 4개 스트림 파일 겹침 없음
  A: concept_parser + image_assist 확장     (src/ 모듈만)
  B: 3탭 골격 + P2/P3/P4               (parser는 mock 주입)
  C: 체크 목록 분해 + R3 사이드바 + P6   (dialog는 아직 보류)
  D: R5 가이드 축소 + R6 요약/4탭
  E: 기존 테스트 영향 조사 + 안전 불변식 테스트 보강

  ── 머지 게이트 1 (총괄+E): D → C(체크목록·R3·P6) → B(골격) → A 순으로 머지
     · 이 순서인 이유: 충돌 반경이 작은 것부터, A는 UI 미접촉이라 마지막이어도 무충돌

Phase 2 — 통합 (약 3일)
  B+A: 빠른 입력 탭에 실제 concept_parser 연결, mock 제거
  C:   st.dialog 전환 (B의 탭 구조 확정 후 — 게이트 조건이 탭 입력과 결합되므로)
  D:   요약 카드에 실데이터 연결 검증
  E:   AppTest 전체 회귀 + E2E

  ── 머지 게이트 2 (총괄+E): B+A 통합 → C dialog

Phase 3 — 검수·마감 (약 2일)
  최종 검수자: §2 체크 5항목 + E2E
  총괄: 문서 갱신(README 사용법, 두 comment 문서에 "반영됨" 표기), 버전 범프(v0.9.0)
```

**의존성 요약** (이것만 지키면 나머지는 자유):
- `C의 dialog` → `B의 탭 구조` 확정 후
- `B의 빠른 입력 실연결` → `A의 parser` 머지 후 (개발은 mock으로 선행 가능)
- `D`는 누구에게도 의존 없음 → 가장 먼저 머지

---

## 4. 인터페이스 계약 (Phase 0에서 동결 — 변경은 총괄 승인 필수)

스트림끼리 코드를 기다리지 않고 병렬로 달리기 위한 합의 지점.

### 4-1. concept_parser 시그니처 (A 제공 → B 소비)

```python
# src/concept_parser.py
def parse_concept_text(
    raw_text: str,
    *,
    llm_call: Callable[[str], str],   # 세션 provider/key로 만든 호출자, B가 주입
) -> ConceptDraft: ...

@dataclass(frozen=True)
class ConceptDraft:
    fields: dict[str, str | list[str]]  # 키는 4-2 화이트리스트만
    fallback_description_only: bool     # 파싱 실패 시 True
```

### 4-2. session_state 키 화이트리스트 (자동 채움 허용 키 — 이 외 주입 금지)

```
kfps_product_category · kfps_fit · kfps_material · kfps_color ·
kfps_season · kfps_occasion · kfps_style_tone ·
kfps_target_hypothesis · kfps_concept_description
```

신규 플래그 키 소유권: `kfps_parse_*`(B) · `kfps_gate_*`(C) · `kfps_has_completed_run`(D set, 전원 read).

### 4-3. ui_text 키 네임스페이스 (copy.py 충돌 방지)

| 스트림 | 접두사 |
|---|---|
| B | `input_tab_*`, `preset_*`, `parse_*` |
| C | `gate_*`, `dialog_*`, `setup_*` |
| D | `summary_*`, `result_tab_*` |

KR/EN 동시 추가 필수. 기존 키 수정은 총괄 승인.

### 4-4. 브랜치·PR 규칙
- 브랜치: `feat/a-parser`, `feat/b-input-tabs`, `feat/c-gate`, `feat/d-results` (스트림당 1개, PR은 P/R 항목당 1개)
- PR 제목에 항목 번호 명시 (예: `[R4] concept inputs 3-tab`)
- 자기 소유 라인 영역 밖 수정이 필요하면 → 해당 스트림에 요청, 직접 수정 금지
- 머지는 총괄만 수행 (게이트 순서 보장)

---

## 5. 리스크와 대응

| 리스크 | 징후 | 대응 |
|---|---|---|
| rendering.py 영역 침범 충돌 | 게이트 1에서 rebase 충돌 | 라인 소유권 재확인, 침범 커밋은 분리 요청 |
| A의 parser 품질 미달 (분해 정확도) | B 통합 시 오채움 빈발 | fallback_description_only 경로가 있으므로 기능 차단 없이 출시 가능 — 프롬프트 튜닝은 후속 |
| st.dialog ↔ AppTest 비호환 | E 회귀 실패 | dialog 내부 로직을 일반 함수로 분리(얇은 래퍼 원칙), 최악 시 R1 dialog만 다음 버전으로 연기 |
| 체크박스 키 제거로 기존 테스트 파손 | Phase 1 E 조사에서 발견 | C가 테스트 수정까지 PR에 포함 |
| copy.py 동시 수정 | 머지마다 충돌 | 네임스페이스 준수 + 게이트 순서 머지로 흡수 |

연기 가능 항목(일정 압박 시 우선 제외): R1 dialog → P2 칩 확대 → P6 프리뷰. **P1/R4(빠른 입력)와 R6/P5(요약)는 연기 불가** — "어렵다" 피드백의 직접 해소 항목.

---

## 6. 완료 기준 (Definition of Done)

- [ ] 신규 사용자 시나리오: 예시 불러오기 → 프리뷰 5명 실행 → 요약 카드 확인까지 **클릭 수 ≤ 6**
- [ ] 텍스트 한 줄 붙여넣기 → 필드 자동 분해 → 수정 → 실행 E2E 통과
- [ ] 이미지 보조: 토글 ON + 세션 key만으로 동작 (env 불필요), OFF 시 기존과 동일
- [ ] 기존 AppTest 전체 + 신규 테스트 통과, raw-image/원문 차단 불변식 테스트 통과
- [ ] 최종 검수자 체크 5항목 승인
- [ ] README 사용법 갱신, v0.9.0 태그

---

## 7. 모델 배정 — 어려운 작업은 Opus, 쉬운 작업은 Sonnet

배정 기준: **설계 판단·함정 회피·프롬프트 품질이 결과를 좌우하면 Opus**,
**기존 패턴 복제·재배치·상수 추가 수준이면 Sonnet**. 스트림 단위가 아니라 항목 단위로 나눈다.

### 7-1. 항목별 배정표

| 항목 | 스트림 | 모델 | 근거 |
|---|---|---|---|
| 총괄: 계약 설계·충돌 중재·게이트 판단 | 총괄 | **Opus** | 스트림 간 트레이드오프 판단, 계약 변경 승인 |
| P1 로직 — concept_parser 프롬프트·파싱·fallback | A | **Opus** | 분해 정확도가 기능 가치 그 자체. 프롬프트 설계 + JSON 강건성 + 실패 경로 설계 |
| P7 — Anthropic/Google analyzer 추가 | A | Sonnet | 기존 `openai_image_analyzer` 패턴 복제 |
| P7 — 세션 key 팩토리·`supports_vision` 플래그 | A | Sonnet | 단순 팩토리 + config 플래그 |
| R4 — 3탭 골격 + state 주입/`st.rerun()` | B | **Opus** | `DuplicateWidgetID`·위젯 렌더 순서 함정, 탭 간 상태 설계가 이후 작업 전체의 기반 |
| P1 UI — 빠른 입력 탭 ↔ parser 연결 | B | **Opus** | R4와 같은 상태 설계 연장선 (동일 작업 흐름으로 묶기) |
| P2 — 칩/프리셋 전환 | B | Sonnet | 기존 `STYLE_TONE_PRESETS` 패턴 복제 + 상수 추가 |
| P3 — 필수 3필드 + 선택 expander | B | Sonnet | 위젯 재배치 |
| P4 — 예시 프리셋 | B | Sonnet | dict → state 주입 버튼 |
| R1 — 체크 목록 분해·표시 | C | Sonnet | 합성 불리언을 이름 있는 리스트로 풀기 |
| R1 — `st.dialog` 비용 확인 전환 | C | **Opus** | AppTest 호환(얇은 래퍼 분리), 게이트 플래그 경로와 결합, 테스트 파손 수습 포함 |
| R3 — 사이드바 슬림화 | C | Sonnet | 함수 내부 재배치 |
| R2 — 준비 체크리스트 칩 | C | Sonnet | 기존 CSS 재사용 신규 컴포넌트 |
| P6 — preview 프리셋 | C | Sonnet | 상수 1개 추가 |
| R6+P5 — 요약 카드·4탭·`st.status` | D | Sonnet | 데이터는 `build_run_report`에 이미 존재, 렌더링 재배치 중심 |
| R5 — 가이드 자동 축소 | D | Sonnet | 플래그 1개 + 분기 |
| QA — 안전 불변식 테스트 설계 (parser 경로 신규) | E | **Opus** | "무엇이 새면 안 되는가"의 경계 정의가 핵심, 누락 시 프로젝트 신뢰 훼손 |
| QA — 회귀 실행·체크리스트 운용 | E | Sonnet | 정해진 절차 수행 |
| 최종 검수 — 5항목 + E2E | 검수자 | **Opus** | 안전 경계·호환 표면·설계 일관성의 종합 판단 |

### 7-2. 운용 원칙

- **Opus 항목 = 6개** (총괄 제외 시 5개): P1 로직, R4+P1 UI, R1 dialog, 불변식 테스트 설계, 최종 검수. 나머지 전부 Sonnet.
- 스트림 안에서 혼합인 경우(A·B·C·E): **Opus로 어려운 항목의 골격을 먼저 만들고, Sonnet이 그 골격 위에서 잔여 항목 처리**. 예: B는 Opus로 R4 탭 구조 확정 → Sonnet으로 P2/P3/P4를 탭 안에 채움.
- **에스컬레이션 규칙**: Sonnet 작업 중 §4 인터페이스 계약을 바꿔야 하는 상황이 오면 즉시 중단하고 Opus(총괄)로 올림 — 계약 변경은 Sonnet 단독 판단 금지.
- Phase별 비중: Phase 1은 Opus 2(P1 로직, R4 골격) + Sonnet 다수 병렬, Phase 2는 Opus 2(P1 연결, dialog), Phase 3은 Opus 1(검수). Opus 작업이 동시 3개를 넘지 않게 분산되어 있음.

---

*총 예상 기간 약 2주 (Phase 0: 0.5일 / Phase 1: 5일 / Phase 2: 3일 / Phase 3: 2일 + 버퍼).
인원 축소 시 병합 우선순위: A+B 겸임 가능(입력 파이프라인), C+D 겸임 가능(앱 흐름). E와 최종 검수자는 분리 유지 권장.*
