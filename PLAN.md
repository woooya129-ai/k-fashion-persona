# PLAN — k-fashion-persona 릴리스 로드맵

본 문서는 `update-PLAN.md`를 PM 관점에서 평가·보강하고, 워크스트림별 역할/병렬 가능성/머지 순서를 못박은 후 버전별로 정리한 정식 릴리스 계획서다.

- 작성자: PM
- 기준 소스: `update-PLAN.md`
- 현재 코드 버전: `0.6.2` (`pyproject.toml`, `src/app_config.py:34`)
- 다음 릴리스: `0.7.0` → `0.7.1` (분리 슬라이스) → `0.8.0` → `0.9.0`
- 문서 상태: 승인 대기 (Approved-by: TBD)

## 문서 변경 이력 (PLAN.md 자체 버전)

| 문서 버전 | 일자 | 변경 |
|---|---|---|
| PLAN v1.0 | 2026-05-18 | `update-PLAN.md` 평가·보강 후 정식 PLAN으로 승격. 4 load-bearing 결정 박음(스키마 잠금, prompt_version bump, public_data 분담, 머지 시퀀스). v0.7.1 슬라이스 분리. |

---

## 0. PM 평가 요약 (update-PLAN.md)

### 0.1 강점

- 제품 정의를 **좁히는** 방향 — "AI 설문 대체"가 아니라 "사전 리스크 점검"으로 재포지셔닝. 이번 분기 가장 큰 회수 포인트다.
- 정부/공공 API를 **점수 보정**이 아니라 **참고 맥락/패널 설명**으로만 쓰는 원칙. 통계 오용 리스크를 사전 차단.
- 이미지 보조 기능을 `v0.7.0`에서 명시적으로 **제외**하고 설계만 가져감. 비용/유출 리스크 회피.
- 워크스트림(WS-0~13)이 잘 분해되어 있고 담당 에이전트가 호명되어 있음.

### 0.2 보강이 필요한 부분 (Gap 매트릭스)

| ID | Gap | 영향 | 본 PLAN에서의 결정 |
|---|---|---|---|
| G1 | WS-1 검증 플래그의 **데이터 거주지 미정** | `EvaluationResult`는 `extra="forbid"` + lock-in v1.2 §3.1로 잠겨 있어 필드 추가 시 스키마 깨짐 (`src/result_parser.py:7-19`) | `AggregateReport`에 `validation_flags: dict[str, list[str]]` 추가. `EvaluationResult` 무변경. §4.1 참고 |
| G2 | WS-6 **prompt_version bump 누락** | `prompt_version`은 `compute_cache_key` 입력 → 같은 파일을 수정하면 의미가 바뀐 결과가 옛 캐시와 충돌 (`prompts/concept_eval_ko_v0_3.md:120-123`, `src/prompt_builder.py:31-38`) | `prompts/concept_eval_ko_v0_4.md`를 **신규 파일**로 추가하고 `PROMPT_VERSION = "concept_eval_ko_v0_4"`로 bump. v0.3 캐시 분리 보장 |
| G3 | WS-10 **신규 `src/public_data/`와 기존 `src/economic_context.py` 관계 미정** | KOSIS hybrid(스냅샷 + statisticsData API + URL 화이트리스트 + cache)가 이미 구현되어 있음 (`src/economic_context.py:1-60`). 중복 구현 위험 | **옵션 B 채택**: `economic_context`는 유지, `src/public_data/`는 행안부/SGIS/상권/기상만. KOSIS 확장은 `economic_context` 내부에서 진행. §4.3 참고 |
| G4 | 파일 핫스팟 **머지 순서 미정** | `aggregator.py`(WS-1,2,3), `rendering.py`(WS-2,3,4,5,5A), `report_writer.py`(WS-1,2,3,11) 4-way 충돌. 동시 PR이면 머지 conflict 반복 | PR 시퀀스 명시 (§5.2) |
| G5 | "오해 문구 없다"는 **측정 불가 DoD** | WS-0 완료 기준이 주관적 | grep-able DoD로 재정의 (§4.0) |
| G6 | "표본 부족 시 인접 연령 보조 포함" **임계값 미정** | 발동 조건/확장폭/표시 방식이 모호 | 임계값: 필터 통과 < 요청 샘플 50%, 확장폭: ±5세, 리포트에 보조 포함 비율 표시 (§4.5A) |
| G7 | "동급 브랜드 가격 위치" 입력의 **사용처 미정** | 프롬프트로 전달이면 D 트랙(WS-6) 의존, 리포트 표시만이면 B 트랙(WS-2/3) 의존 | **리포트 표시만**. 프롬프트에는 전달하지 않음(LLM 환각 위험 회피). §4.5 참고 |
| G8 | **API 키 부재 시 동작** 회귀 테스트 미정 | HF Space에 키 없는 경우 fallback 경로가 깨지면 공개 데모가 죽음 | KOSIS/행안부 모두 `MISSING_API_KEY → snapshot fallback → 리포트에 "참고 통계 미사용" 표시`를 fixture 테스트로 못박음 (§4.7) |
| G9 | **롤백/feature flag 정책** 미정 | 검증 플래그가 노이즈 폭증 시 사용성 저하 | 환경변수 `K_FASHION_VALIDATION_FLAGS=on|off`(기본 on)로 끌 수 있게. §4.8 참고 |
| G10 | 행안부 API **인증 방식 차이** 미반영 | KOSIS는 URL `serviceKey` param, 행안부는 공공데이터포털 발급 키. 공통 connector가 일률 가정하면 깨짐 | `src/public_data/` connector 추상화에 **인증 어댑터** 인터페이스를 두고 KOSIS/행안부 각각 구현 (§4.10) |
| G11 | WS-7 QA **fixture/회귀 케이스 수 미정** | "테스트 여러 개"는 측정 불가 | 최소 케이스 목록을 §4.7에 명시 |
| G12 | WS-11(행안부) **v0.7.0 동시 진행 리스크** | KOSIS 확장 + 공통 기반 + 행안부 신규 API + UI 패널 분포까지 한 릴리스에 묶으면 일정 리스크 큼 | **v0.7.1로 분리** — 행안부 API + 패널 분포 비교를 별도 슬라이스 (§3) |

### 0.3 PM 결정 (update-PLAN 대비 변경)

1. **EvaluationResult 무변경**. 검증 플래그는 `AggregateReport`에 저장.
2. **prompt_version bump**: `concept_eval_ko_v0_3` → `concept_eval_ko_v0_4`. 신규 파일 추가.
3. **`economic_context` 유지**. 신규 `src/public_data/`는 행안부/SGIS/상권/기상 전용.
4. **v0.7.1 슬라이스 분리**: WS-11(행안부)을 별도 릴리스로. v0.7.0은 KOSIS 확장까지.
5. **머지 순서**: D → A → C → B → E → F (§5.2).
6. **검증 플래그 feature flag**: `K_FASHION_VALIDATION_FLAGS` 환경변수 도입.
7. **"동급 브랜드 가격 위치"**: 리포트 표시 전용. 프롬프트 미전달.

---

## 1. 제품 정의 (불변)

> 실제 설문 전에, 합성 페르소나로 제품 컨셉의 **리스크 질문**을 빨리 뽑는 도구.

### 1.1 성공 기준

- "AI 설문조사 대체"로 오해될 표현이 README/UI/리포트에서 grep 0건.
- 결과 상단에서 한계와 검증 필요 지점을 3초 안에 본다.
- 누가 포함된 패널인지(성별/연령/직업/지역/실제 샘플 수) 분포가 모든 리포트에 표시된다.
- 입력에 없는 가격/디자인/성별/착용상황 환각은 검증 플래그로 표시된다.
- 디자이너가 다음 설문/품평에서 확인할 질문을 1개 이상 얻는다.

### 1.2 비목표 (Non-goals, v0.7.x)

- 이미지 업로드 직접 평가
- 실제 판매·구매율 예측 표현
- 무신사 등 민간 데이터 연동
- 복잡한 가중 샘플링 UI
- 지도 기반 리포트

---

## 2. 워크스트림 → 트랙 매핑

워크스트림 ID는 update-PLAN.md를 그대로 승계한다. 트랙은 본 PLAN에서 새로 부여한다.

| 트랙 | 성격 | WS | 주 파일 | 다른 트랙과의 충돌 |
|---|---|---|---|---|
| **A** | Copy/문구 | WS-0 | `src/ui/copy.py`, `README.md`, `docs/README-ENG.md`, `docs/INSTALL.md` | 거의 없음 — 가장 먼저 또는 병렬 가능 |
| **B** | Backend chain (직렬) | WS-1 → WS-2 → WS-3 | `src/aggregator.py`, `src/result_parser.py`(읽기만), `src/report_writer.py` | E의 `report_writer.py` 섹션 추가와 머지 순서 합의 |
| **C** | Input UX chain (직렬) | WS-4 → WS-5 → WS-5A | `src/ui/rendering.py`, `src/persona_filter.py`, `src/app_config.py`, (선택) `src/prompt_builder.py` | B와 `rendering.py` 충돌 — **C 먼저 머지** |
| **D** | Prompt | WS-6 | `prompts/concept_eval_ko_v0_4.md`(신규), `src/prompt_builder.py`(상수 1줄), `tests/test_prompt_builder.py` | 거의 독립 |
| **E** | Public Data | WS-10 → WS-11 (v0.7.1로 분리) | `src/public_data/`(신규), `src/report_writer.py`, `src/ui/rendering.py`(섹션 추가) | B의 `report_writer.py`에 적층 — B 머지 후 진입 |
| **F** | QA/Release | WS-7, WS-8 | `tests/`, `pyproject.toml`, `docs/CHANGELOG.md` | 모든 트랙 종속 |

### 2.1 병렬 가능 시점

- **T0 (릴리스 시작 직후)**: A, C, D, E(WS-10 공통 기반)를 동시 시작. B(WS-1)는 단독 시작.
- **T1 (B 1차 머지 후)**: E(WS-11) 진입 가능.
- **T2 (B/C/E 머지 완료 후)**: F 진입.

### 2.2 WS별 PM 평가 (난이도/병렬도)

| WS | update-PLAN 평가 | PM 보강 평가 |
|---|---|---|
| WS-0 | 낮음 | 적정. 단 grep-able DoD 필요 (G5) |
| WS-1 | 높음 | **데이터 거주지 결정 필수** (G1) → `AggregateReport.validation_flags`. feature flag 필수 (G9) |
| WS-2 | 중간 | 적정. WS-1 자료구조 위에 적층되므로 직렬 |
| WS-3 | 중간 | 적정. **새 LLM 호출 금지** 원칙 유지 |
| WS-4 | 중간 | 적정 |
| WS-5 | 중간 | **G7 결정**: 가격 위치는 리포트 전용, 프롬프트 미전달 |
| WS-5A | 중간 | 적정. **G6 결정**: 인접 연령 보조 임계값 명시 |
| WS-6 | 낮음 | **prompt_version bump 명시** (G2) — 난이도 자체는 낮음 |
| WS-7 | 높음 | **fixture 최소 목록 명시** (G11) |
| WS-8 | 낮음 | 적정. **롤백 정책 추가** (G9) |
| WS-9 | 중간 | 적정. v0.7.0 구현 미포함, 문서 산출물 1개로 한정 |
| WS-10 | 높음 | **economic_context와 분담 명시** (G3) — 옵션 B |
| WS-11 | 높음 | **v0.7.1로 분리** (G12) |
| WS-12 | 높음 | v0.8.0 적정 |
| WS-13 | 중간 | v0.9.0 적정 |

---

## 3. 버전별 릴리스 로드맵

### 3.1 v0.7.0 — 신뢰도 회수 (제품 정의 + 검증 방어선 + 입력 구조 + KOSIS 확장)

**테마**: 결과를 "정답"이 아니라 "검증해야 할 리스크 질문"으로 읽게 만든다.

**포함**:

- WS-0 제품 포지션/한계 문구 통일 (Track A)
- WS-1 사후 검증 플래그 (Track B, `AggregateReport.validation_flags`)
- WS-2 패널 분포 표시 (Track B)
- WS-3 결과 상단 세줄요약 (Track B)
- WS-4 디자인 디테일 입력 (Track C)
- WS-5 스타일 톤/가격 위치 입력 (Track C, 리포트 전용)
- WS-5A 연령 범위 슬라이더 + 직접 입력 (Track C)
- WS-6 프롬프트 안전 규칙 강화 (Track D, **prompt_version bump**)
- WS-9 이미지 보조 설계 문서 (구현 없음)
- WS-10 정부/공공 API 공통 기반 (Track E, **행안부/SGIS/상권/기상용**)
- KOSIS OpenAPI 확장 (`economic_context` 내부 — 새 디렉토리 아님)
- WS-7 QA 회귀 (Track F)
- WS-8 릴리스 (Track F)

**제외 (v0.7.0)**:

- 행안부 주민등록 인구 API (→ v0.7.1)
- SGIS/상권/기상 (→ v0.8.0)
- 이미지 보조 구현 (→ v0.8.0 후보)

**완료 기준 (v0.7.0)**:

- 모든 `update-PLAN.md` 릴리스 체크리스트 항목 중 v0.7.0 범위 통과
- `EvaluationResult` 스키마 무변경 (lock-in v1.2 §3.1 준수)
- `prompt_version = concept_eval_ko_v0_4`, v0.3 캐시와 자동 분리
- KOSIS API 키 부재 시 스냅샷 fallback 동작 fixture 테스트 통과
- README/copy.py/footer/리포트 4곳에서 "합성 페르소나 기반 사전 리스크 점검" 문구 노출, forbidden phrase grep 0건

### 3.2 v0.7.1 — 패널 신뢰도 슬라이스 (행안부 인구 통계)

**테마**: 합성 패널이 실제 인구 분포와 어떻게 다른지 보여준다.

**포함**:

- WS-11 행안부 주민등록 인구 API 연결 (Track E)
- 연령/성별/지역 인구 분포 비교 섹션을 리포트에 추가
- 인증 어댑터 패턴 확립 (KOSIS와 다른 인증 방식 흡수)

**제외**:

- 점수 보정 (참고 표시만)
- 지도 UI

**완료 기준**:

- 행안부 API 키 부재 시도 앱 실행 유지
- 선택 연령 범위와 전체 인구 기준 분포가 같은 리포트 표에 표시됨
- 리포트에 인구 API 호출 상태(성공/실패), 출처, 기준일 표시

### 3.3 v0.8.0 — 컨텍스트 확장

**테마**: 지역/시즌 맥락을 선택적으로 붙인다.

**포함**:

- WS-12 SGIS S-Open API (지역 입력 있을 때만)
- 소상공인 상가(상권)정보 API (지역 입력 있을 때만)
- 기상청 단기예보/기상자료 API (시즌성 상품일 때만)
- WS-9 이미지 기반 컨셉 설명 보조 **구현** (토글 OFF 기본, 1회 호출 보장)

**완료 기준**:

- 모든 신규 API가 "참고 섹션"으로만 등장
- 이미지 보조: 페르소나 평가 호출마다 이미지를 보내는 구조가 코드 레벨에서 불가능 (호출 경계 가드 + 테스트)

### 3.4 v0.9.0 — 거시 맥락

**테마**: 생활물가/거시경제 참고를 상세 리포트 전용으로.

**포함**:

- WS-13 한국소비자원 참가격 API
- 한국은행 ECOS API

**완료 기준**:

- 기본 리포트에서 접힘, 상세 리포트 토글로만 노출
- 의류 직접 가격 비교로 오해될 섹션은 자동 숨김

---

## 4. 보강 가이드 (load-bearing 결정)

### 4.1 [G1] 검증 플래그 데이터 거주지 — `AggregateReport.validation_flags`

**결정**: `EvaluationResult`는 무변경. 검증 플래그는 결과 집계 단계에서 deterministic 후처리로 생성하고 `AggregateReport`에 저장.

권장 스키마:

```python
# src/aggregator.py 내 AggregateReport에 필드 추가
validation_flags: dict[str, list[str]]
# 예시:
# {
#   "price_mismatch_possible": ["persona_id_1", "persona_id_7"],
#   "uninput_design_element_mentioned": ["persona_id_3"],
#   "gender_context_mismatch_possible": [],
#   "occasion_mismatch_possible": ["persona_id_5"],
# }
```

플래그 키 4종(v0.7.0 초안):

- `price_mismatch_possible` — 입력 가격과 LLM 응답 텍스트의 가격 단어 충돌 가능성
- `uninput_design_element_mentioned` — 디자인 디테일 체크박스에 없는 요소(그래픽/패턴/로고/자수/프린트/워싱) 언급
- `gender_context_mismatch_possible` — 제품 성별과 페르소나 성별 텍스트 충돌
- `occasion_mismatch_possible` — 착용 상황 입력과 LLM 응답의 사용 상황 텍스트 충돌

표현 원칙: "오류"가 아니라 "가능성". UI/리포트에 `검증 필요 가능성: N건`으로 표시.

### 4.2 [G2] prompt_version bump

**결정**: `prompts/concept_eval_ko_v0_4.md` 신규 파일. `src/prompt_builder.py`에서 `PROMPT_VERSION = "concept_eval_ko_v0_4"`, `SUPPORTED_PROMPT_VERSIONS`에 추가.

이유: `prompt_version`은 `compute_cache_key` 입력(`prompts/concept_eval_ko_v0_3.md:120-123` cache invalidation 규칙). 같은 파일을 수정하면 의미가 바뀐 결과가 옛 캐시와 충돌.

v0_4의 변경점 (WS-6):

- 입력에 없는 디자인 요소 생성 금지 규칙 추가
- 입력 가격과 다른 가격대로 평가 금지 규칙 추가
- 제품 성별과 다른 착용 상황 생성 금지 규칙 추가
- v0_3의 균형형 평가 톤은 유지

### 4.3 [G3] `src/public_data/` vs `src/economic_context.py` 분담

**결정 (옵션 B)**: `economic_context`는 KOSIS 전용으로 유지·확장. 신규 `src/public_data/`는 행안부/SGIS/상권/기상 등 **추가 API** 전용.

이유: KOSIS hybrid는 이미 lock-in 계약(URL 화이트리스트, 스냅샷 hash, cache 키)이 박혀 있어 이전 비용이 크다.

`src/public_data/` 구조 (제안):

```
src/public_data/
  __init__.py
  base.py            # PublicDataConnector 추상 클래스, AuthAdapter
  cache.py           # 응답 캐시 (메모리 + 파일)
  source.py          # SourceMetadata (출처/기준일/호출 상태)
  errors.py
  population/        # 행안부 (v0.7.1)
    connector.py
    fixtures/
  spatial/           # SGIS (v0.8.0)
  commercial/        # 상권정보 (v0.8.0)
  weather/           # 기상청 (v0.8.0)
```

KOSIS 확장(v0.7.0)은 **`src/economic_context.py` 내부**에서 진행하고, 향후 v1.x 정리 시점에 `src/public_data/kosis/`로 facade 통합을 검토한다(이번 분기 범위 아님).

### 4.4 [G4] 머지 순서 — §5.2 참고

### 4.5 [G7] "동급 브랜드 가격 위치" — 리포트 전용

**결정**: 입력값은 받되 LLM 프롬프트에는 전달하지 않는다. 리포트의 "가격 부담 해석" 섹션 옆에 "동급 브랜드 기준 사용자 자가 평가"로만 표시.

이유: 프롬프트로 전달하면 LLM이 자체 가격대 추론을 시도하여 환각 위험 증가. 사용자 자가 분류는 디자이너 의사결정 보조 정보로만 충분하다.

저장 위치: `AggregateReport.input_snapshot` 또는 별도 메타 필드(아키텍처는 구현 시점에 확정).

### 4.5A [G6] 표본 부족 시 인접 연령 보조 — 임계값

**결정**:

- **발동 조건**: 필터 통과 페르소나 수 < 요청 샘플 수의 50%
- **확장폭**: 하한 −5세, 상한 +5세 (1회만)
- **재발동**: 1회 확장 후에도 70% 미만이면 추가 확장 없이 **부족 상태로 표시**
- **리포트 표시**: "보조 포함 비율: N% (±5세 확장으로 추가된 페르소나)" 고정 노출

### 4.6 [G5] WS-0 grep-able DoD

| DoD | 검증 명령 |
|---|---|
| README/copy.py/docs/footer 4곳에 "합성 페르소나 기반 사전 리스크 점검" 노출 | `grep -r "합성 페르소나 기반 사전 리스크 점검" README.md src/ui/copy.py docs/ src/report_writer.py` ≥ 4 |
| forbidden phrase 0건 | `report_writer.FORBIDDEN_PHRASES`에 "AI 설문조사", "구매율 예측", "판매 가능성 예측" 추가 + 리포트 회귀 테스트 |
| 리포트 푸터에 한계 문구 노출 | `required_footer_text()` 출력 회귀 fixture |

### 4.7 [G8, G11] 회귀 테스트 최소 목록 (WS-7)

| 테스트 카테고리 | 최소 케이스 수 | 비고 |
|---|---:|---|
| 검증 플래그 (`AggregateReport.validation_flags`) | 4 (플래그 키당 1) | positive/negative 모두 |
| 패널 분포 표시 (`tests/test_report_writer.py`) | 3 | 단일 성별, 단일 연령대, 보조 확장 발동 |
| 세줄요약 (`tests/test_aggregator.py`) | 2 | 긍정 우세, 검증 필요 우세 |
| 연령 슬라이더-직접 입력 동기화 (`tests/test_app.py`) | 3 | 프리셋→슬라이더, 슬라이더→직접 입력, 하한>상한 보정 |
| prompt_version bump (`tests/test_prompt_builder.py`) | 2 | v0_3/v0_4 cache key 분리 검증 |
| forbidden phrases (`tests/test_report_writer.py`) | 신규 phrase당 1 | 신규 추가 phrase 회귀 |
| **API 키 부재 fallback** (`tests/`) | 2 | KOSIS, 행안부(v0.7.1) — `MISSING_API_KEY → snapshot/`"참고 통계 미사용"` |
| **feature flag** (`K_FASHION_VALIDATION_FLAGS`) | 2 | on/off 동작 |

### 4.8 [G9] feature flag 정책

```bash
# 기본값: on
# 검증 플래그가 노이즈 폭증할 때 사용자가 끌 수 있게
K_FASHION_VALIDATION_FLAGS=on|off
```

`off` 시 `AggregateReport.validation_flags`는 빈 dict로 채워지고 UI/리포트의 검증 섹션은 숨김. 회귀 테스트로 동작 보장.

### 4.10 [G10] 인증 어댑터 인터페이스 (v0.7.1 준비)

`src/public_data/base.py`에 어댑터 인터페이스:

```python
class AuthAdapter(Protocol):
    def apply(self, url: str, params: dict) -> tuple[str, dict]: ...

class KosisAuthAdapter:  # serviceKey URL param
class DataGoKrAuthAdapter:  # 공공데이터포털 인증키
```

v0.7.0에서 인터페이스만 잡고, 구현은 v0.7.1(행안부)에서 첫 사례로 박는다.

---

## 5. 역할 분담과 병렬 진행 분석

### 5.1 트랙별 담당 에이전트

| 트랙 | 담당 에이전트 (update-PLAN.md 승계) | 비고 |
|---|---|---|
| A | PM Copy Agent | grep-able DoD 적용 |
| B | Backend Validation Agent (WS-1) → Data Reporting Agent (WS-2) → Report UX Agent (WS-3) | 한 트랙 내부 직렬 — 동시 진행 금지 |
| C | Input UX Agent (WS-4, WS-5A), Input Strategy Agent (WS-5) | 트랙 내부 PR 분리 가능하나 `rendering.py` 충돌 주의 |
| D | Prompt Agent | `prompt_version` bump 책임 |
| E | Public Data Platform Agent (WS-10), Population Data Agent (WS-11, v0.7.1) | KOSIS 확장은 `economic_context` 담당자(별도)에게 |
| F | QA Agent (WS-7), Release Agent (WS-8) | 전 트랙 종속 |

### 5.2 파일 충돌 매트릭스와 머지 순서

| 파일 | 수정 트랙 | 머지 순서 |
|---|---|---|
| `src/ui/copy.py`, `README.md`, `docs/*` | A | (1) 가장 먼저 — 충돌 없음 |
| `src/ui/rendering.py` | A, C, B(WS-2/3 일부) | (2) C 머지 (T0~T1) |
| `src/persona_filter.py`, `src/app_config.py` | C | (2) C 머지 (T0~T1) |
| `prompts/concept_eval_ko_v0_4.md` (신규) | D | (3) D 머지 (T0~T1) — 신규 파일이라 충돌 없음 |
| `src/prompt_builder.py` (상수 1줄) | D | (3) D 머지 (T0~T1) |
| `src/aggregator.py` | B | (4) B WS-1 → WS-2 → WS-3 직렬 머지 |
| `src/report_writer.py` | B, E | (4) B 머지 후 (5) E가 적층 |
| `src/public_data/` (신규 디렉토리) | E | (5) B 머지 후 진입 |
| `tests/` | F | (6) 모든 트랙 머지 후 |
| `pyproject.toml`, `docs/CHANGELOG.md`, 버전 상수 | F | (6) 마지막 |

**권장 시퀀스**:

```
T0:  D 시작 (prompt v0_4) ─┐
     A 시작 (copy/문구)    ├─ 병렬
     C 시작 (input UX)     │
     E 시작 (WS-10 공통)   ┘
     B 시작 (WS-1만)  ─ 단독 시작

T1:  D 머지 → A 머지 → C 머지 → B(WS-1) 머지
     B(WS-2) 시작 → 머지
     B(WS-3) 시작 → 머지
     E(KOSIS 확장) 머지

T2:  F 진입 (QA + Release)
     v0.7.0 태깅

v0.7.1 슬라이스:
     E(WS-11 행안부) 시작 → 머지 → F → 태깅
```

### 5.3 진정한 병렬 가능 구간

- **완전 병렬 가능**: A ↔ C ↔ D ↔ E(공통 기반)
- **단독 시작 가능**: B(WS-1)
- **머지 후 진입 필요**: E(KOSIS 확장은 economic_context 별도, report_writer 섹션 추가는 B 머지 후)
- **항상 마지막**: F

병렬 작업자 수 권장: **3~4명**까지는 머지 충돌 최소화. 그 이상은 같은 파일 핫스팟에서 conflict 빈발.

---

## 6. 워크스트림 카드 (보강 후)

각 카드는 update-PLAN.md의 원본을 기반으로 PM 결정과 측정 가능한 DoD를 추가했다.

### WS-0 제품 포지션/한계 문구 (Track A)

- **DoD (grep-able)**: §4.6 표
- **주의**: forbidden phrase에 신규 추가 시 기존 fixture 전수 갱신 필요

### WS-1 사후 검증 플래그 (Track B)

- **데이터 거주지**: `AggregateReport.validation_flags: dict[str, list[str]]` — `EvaluationResult` 무변경
- **플래그 키 4종**: §4.1 참고
- **feature flag**: `K_FASHION_VALIDATION_FLAGS=on|off` (기본 on)
- **DoD**: 4개 플래그 모두 fixture로 positive/negative 케이스 확보

### WS-2 패널 분포 표시 (Track B, WS-1 머지 후)

- 성별/연령/직업/지역/실제 샘플 수 + 보조 확장 비율(§4.5A)
- **DoD**: 단일 성별/단일 연령/보조 확장 발동 3 케이스 회귀

### WS-3 결과 상단 세줄요약 (Track B, WS-2 머지 후)

- **원칙**: 신규 LLM 호출 금지. 기존 집계값(sentiment 분포, validation_flags 카운트, 보조 포함 비율)에서 deterministic 생성
- **DoD**: 긍정 우세/검증 필요 우세 2 케이스 회귀

### WS-4 디자인 디테일 입력 (Track C)

- 체크박스 7개 + 자유 입력 + "장식 없음"을 구조화 입력으로 저장
- **DoD**: 체크박스 미선택 시 `AggregateReport.input_snapshot.design_details = []`가 LLM 프롬프트와 검증 플래그 양쪽에서 동일하게 해석됨

### WS-5 타깃/가격 맥락 입력 (Track C)

- **결정 (§4.5)**: 동급 브랜드 가격 위치는 **리포트 전용**. 프롬프트 미전달
- 베타 연령대 프리셋 (전체/10-20/20-30/30-40/40+)
- **DoD**: 프리셋 선택값이 WS-5A 슬라이더와 동기화

### WS-5A 연령 범위 슬라이더 + 직접 입력 (Track C)

- 하한/상한 슬라이더 2개 + 숫자 입력 2개 (구현 제약 시 단일 range slider 대안)
- 10단위 스텝 + 1세 단위 직접 입력 + 동기화 + 하한>상한 보정
- **DoD**: §4.7 표 3 케이스

### WS-6 프롬프트 안전 규칙 강화 (Track D)

- **prompt_version bump**: `concept_eval_ko_v0_4` (§4.2)
- 신규 규칙: 입력 외 디자인 요소 생성 금지, 입력 가격대 외 평가 금지, 제품 성별과 다른 착용 상황 생성 금지
- **DoD**: v0_3/v0_4 cache key 분리 검증 fixture

### WS-7 QA/회귀 (Track F)

- **최소 케이스**: §4.7 표
- 가격 오독, 미입력 그래픽 언급, 성별 맥락 오류, 보조 확장 발동을 모두 포함

### WS-8 릴리스 (Track F)

- `pyproject.toml`, `src/app_config.py:34` (`APP_VERSION`), README 배지, `docs/CHANGELOG.md`, `docs/README-ENG.md`
- **롤백 정책**: 검증 플래그 노이즈 폭증 시 `K_FASHION_VALIDATION_FLAGS=off`로 즉시 비활성 가능

### WS-9 이미지 보조 설계 문서 (구현 없음, v0.7.0)

- 산출물 1개: `docs/design/image-concept-assist.md` (제안 경로)
- 토글 OFF 기본, 1회 호출 보장, 페르소나 평가에 텍스트만 전달, 저장하지 않음, HF Space 경고 문구

### WS-10 공통 API 기반 (Track E, v0.7.0)

- **범위 (§4.3)**: 행안부/SGIS/상권/기상 전용. KOSIS는 `economic_context`에서 별도 확장
- `src/public_data/` 구조 §4.3 참고
- 인증 어댑터 인터페이스 §4.10
- **DoD**: 네트워크 없이 fixture로 호출/실패/캐시 회귀 통과

### WS-11 행안부 인구 API (Track E, **v0.7.1로 분리**)

- 분리 이유: §0.2 G12 — v0.7.0에 묶으면 일정 리스크 큼
- 인증 어댑터 첫 구현
- 패널 분포 ↔ 인구 분포 비교 섹션을 리포트에 추가

### WS-12 SGIS/상권/기상 (v0.8.0)

- 지역 입력 있을 때만 호출. 전국 타깃이면 호출 안 함
- 시즌성 강한 상품일 때만 날씨 섹션 표시
- 점수 보정 금지 — 참고 섹션만

### WS-13 참가격/ECOS (v0.9.0)

- 기본 리포트 접힘, 상세 리포트 토글
- 의류 직접 가격 비교로 오해될 섹션 자동 숨김

---

## 7. 우선순위

update-PLAN.md의 우선순위를 PM 결정에 맞춰 정리. v0.7.0 범위만.

| 우선순위 | 항목 | 트랙 | 이유 |
|---:|---|---|---|
| P0 | 제품 포지션 문구 (WS-0) | A | 오해를 줄이지 않으면 이후 기능도 "정확도 실패"로 읽힌다 |
| P0 | 사후 검증 플래그 (WS-1) | B | 틀린 결과를 그대로 보여주는 문제를 막는다 |
| P0 | prompt_version bump (WS-6) | D | 캐시 계약 위반 방지 |
| P1 | 패널 분포 표시 (WS-2) | B | "누구에게 물었는지" 불신 회수 |
| P1 | 세줄요약 (WS-3) | B | 긴 리포트 전에 핵심 |
| P1 | 연령 범위 UI (WS-5A) | C | 베타 사용자가 직접 요구한 기능 |
| P1 | 공통 API 기반 (WS-10) | E | 후속 API 카오스 방지 |
| P1 | KOSIS 확장 | (econ_context) | 가격·소비 기준값 강화 |
| P2 | 디자인 디테일 입력 (WS-4) | C | 패션 컨셉 평가 핵심 맥락 |
| P2 | 스타일 톤/가격 위치 (WS-5) | C | 보조 맥락 — 리포트 전용 |
| P2 | feature flag (G9) | B | 롤백 안전망 |
| P3 | 이미지 보조 설계 (WS-9) | docs | 문서만, v0.8.0 후보 |

---

## 8. 리스크와 대응 (보강)

| 리스크 | 대응 |
|---|---|
| `EvaluationResult` 스키마에 필드 추가 PR 유입 | PR 템플릿/리뷰 가이드에 "스키마 잠금" 박음. `AggregateReport`로 우회 |
| `prompts/concept_eval_ko_v0_3.md` 직접 수정 PR 유입 | PR 리뷰 단계에서 거부. 신규 `_v0_4.md` + `PROMPT_VERSION` 동시 변경만 허용 |
| 검증 플래그가 너무 많이 뜸 | "오류"가 아니라 "검증 필요 가능성"으로 표현 + `K_FASHION_VALIDATION_FLAGS=off` 즉시 비활성 |
| 패널 분포가 실제 고객처럼 오해됨 | 모든 분포 표에 "합성 페르소나 기준" 문구 고정 |
| 디자인 디테일 입력 복잡 | 체크박스 7개 + 자유 입력 1개로 제한 |
| 연령 필터로 표본 부족 | §4.5A 임계값 + 보조 포함 비율 리포트 노출 |
| 연령 슬라이더-직접 입력 충돌 | 단일 상태값 기준 동기화, 하한>상한 자동 보정 |
| 프롬프트 강화만 믿게 됨 | 사후 검증을 P0로 유지 |
| KOSIS/행안부 API 키 부재 | 스냅샷 fallback + "참고 통계 미사용" 표시 + fixture 회귀 |
| 행안부 인증 방식 차이 | §4.10 어댑터 인터페이스 |
| 머지 conflict 다발 | §5.2 머지 시퀀스 강제. 동일 핫스팟 동시 PR 금지 |
| v0.7.0 일정 리스크 | WS-11(행안부)을 v0.7.1로 분리 |
| HF Space와 GitHub 커밋 SHA 불일치 | 콘텐츠 기준 확인 (`docs/CHANGELOG.md` 버전 일치) |
| 이미지 보조가 평가 기능으로 오해됨 | 기능명 "이미지 기반 컨셉 설명 보조"로 한정, 기본 OFF, v0.7.0 구현 없음 |

---

## 9. 릴리스 체크리스트

### 9.1 v0.7.0

- [ ] `pyproject.toml` 버전 `0.7.0`
- [ ] `src/app_config.py` `APP_VERSION = "0.7.0"`
- [ ] `src/ui/copy.py` `hero_eyebrow` 버전 갱신
- [ ] README 버전 배지 `0.7.0`
- [ ] `docs/README-ENG.md` 버전 배지 `0.7.0`
- [ ] `docs/CHANGELOG.md`에 `v0.7.0` 항목 추가
- [ ] `prompts/concept_eval_ko_v0_4.md` 신규 추가
- [ ] `src/prompt_builder.py` `PROMPT_VERSION = "concept_eval_ko_v0_4"`, `SUPPORTED_PROMPT_VERSIONS` 갱신
- [ ] `src/aggregator.py` `AggregateReport.validation_flags` 추가
- [ ] `src/result_parser.py` `EvaluationResult` 무변경 확인
- [ ] `K_FASHION_VALIDATION_FLAGS` 환경변수 처리 추가
- [ ] 리포트 푸터 한계 문구 4곳 노출 (grep ≥4)
- [ ] forbidden phrase 추가 (`AI 설문조사`, `구매율 예측`, `판매 가능성 예측`)
- [ ] 패널 분포 UI 확인 (성별/연령/직업/지역/실제 샘플 수 + 보조 확장 비율)
- [ ] 연령 범위 슬라이더/직접 입력 동기화 확인
- [ ] 디자인 디테일 체크박스 7개 + 자유 입력 + "장식 없음" 구조화
- [ ] 동급 브랜드 가격 위치 입력 (리포트 표시 전용, 프롬프트 미전달)
- [ ] 정부/공공 API 공통 기반 추가 (`src/public_data/`)
- [ ] KOSIS OpenAPI 확장 (economic_context)
- [ ] API 실패 시 앱 실행과 리포트 생성 유지 확인 (fixture)
- [ ] API 출처/기준일/호출 상태 리포트 표시 확인
- [ ] WS-9 이미지 보조 설계 문서 작성 (`docs/design/image-concept-assist.md`)
- [ ] 회귀 테스트 §4.7 통과
- [ ] 리포트 예시 최신화
- [ ] GitHub `main` push
- [ ] HF Space 업로드 및 README 렌더 확인 (콘텐츠 기준)

### 9.2 v0.7.1 (행안부 슬라이스)

- [ ] `pyproject.toml` 버전 `0.7.1`
- [ ] `src/app_config.py` `APP_VERSION = "0.7.1"`
- [ ] `src/public_data/population/` 추가
- [ ] 인증 어댑터 (`KosisAuthAdapter`, `DataGoKrAuthAdapter`)
- [ ] 행안부 API 키 부재 시 fallback 확인
- [ ] 패널 분포 ↔ 인구 분포 비교 섹션 리포트 추가
- [ ] `docs/CHANGELOG.md` v0.7.1 항목

### 9.3 v0.8.0 / v0.9.0

- 별도 PLAN 업데이트로 상세화. 본 PLAN.md는 스코프와 완료 기준만 §3에 박는다.

---

## 부록 A — update-PLAN.md → PLAN.md 변경 요약

본 PLAN.md가 `update-PLAN.md`와 다른 지점만 명시.

| 항목 | update-PLAN.md | PLAN.md (본 문서) |
|---|---|---|
| 검증 플래그 거주지 | 미정 | `AggregateReport.validation_flags` |
| prompt_version | v0_3 수정 표현 | **v0_4 신규** + bump |
| 공통 API 기반 vs economic_context | 미정 | **옵션 B**: economic_context 유지, public_data는 신규 API만 |
| 행안부 API | v0.7.0 포함 | **v0.7.1로 분리** |
| 가격 위치 입력 사용처 | 미정 | **리포트 전용**, 프롬프트 미전달 |
| 보조 연령 확장 임계값 | 미정 | 통과 < 50% 시 ±5세 |
| feature flag | 없음 | `K_FASHION_VALIDATION_FLAGS` 추가 |
| WS-0 DoD | 주관적 | grep-able 4곳 |
| QA fixture 수 | "여러 개" | §4.7 표 (정량) |
| 머지 순서 | 미정 | §5.2 시퀀스 |
| 인증 어댑터 | 미정 | KOSIS/DataGoKr 어댑터 분리 |
