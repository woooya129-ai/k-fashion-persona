# SPDX-License-Identifier: AGPL-3.0-only
"""Localized UI copy for the Streamlit app."""

from __future__ import annotations

UI_COPY: dict[str, dict[str, str]] = {
    "KR": {
        "nav_brand": "k-fashion-persona",
        "nav_concept": "컨셉",
        "nav_panel": "패널",
        "nav_model": "모델",
        "nav_report": "리포트",
        "subnav_title": "k-fashion-persona",
        "subnav_local": "로컬 실행",
        "subnav_keys": "키 비공개",
        "subnav_panel": "합성 패널",
        "subnav_run": "실행",
        "hero_title": "k-fashion-persona",
        "intro_badge": "NVIDIA 제작 · 한국 공공데이터 분포 기반",
        "intro_title": "한국형 합성 페르소나로 패션 컨셉을 먼저 검토한다",
        "intro_body": (
            "Nemotron-Personas-Korea는 NVIDIA가 만든 완전 합성 페르소나 데이터셋이야. "
            "KOSIS, 대법원, 국민건강보험공단, 한국농촌경제연구원 등 한국 공공데이터의 "
            "분포를 참고해 한국 사용자 맥락을 더 잘 반영하도록 설계됐어."
        ),
        "api_intro_title": "먼저 확인: API와 요금",
        "api_intro_body": (
            "실행하면 선택한 LLM provider API로 요청이 나가고, 입력/출력 토큰 단가와 "
            "패널 수로 비용을 추정해. 실제 청구는 provider 공식 요금과 계정 조건을 따라."
        ),
        "api_intro_1": "API key는 화면에 그대로 노출하지 않음",
        "api_intro_2": "패널 수가 늘수록 호출 수와 비용 증가",
        "api_intro_3": "실행 전 예상 비용 확인 체크 필요",
        "hero_main": "설문 전, 먼저 반응을 읽다",
        "hero_subtext": (
            "합성 페르소나 기반 사전 리스크 점검으로 "
            "전문 설문이나 본조사 전 반응의 흐름을 빠르게 확인합니다."
        ),
        "hero_eyebrow": "로컬 퍼블릭 베타 · v0.8.0",
        "hero_pill_1": "로컬 실행",
        "hero_pill_2": "원문 저장 없음",
        "hero_pill_3": "리포트 내보내기",
        "hero_pill_4": "🤗 nvidia/Nemotron-Personas-Korea",
        "hero_pill_5": "GitHub",
        "hero_pill_docs": "Docs",
        "hero_pill_license": "AGPL-3.0-only",
        "hero_docs_aria": "정적 설명 페이지 (docs) 열기",
        "hero_license_aria": "GitHub LICENSE 파일 열기",
        "cost_confirm_toast": "실행하려면 예상 비용·시간 확인에 체크해 주세요.",
        "job_already_running": "이미 실행 중인 작업이 있어요. 취소하거나 완료를 기다려 주세요.",
        "guide_eyebrow": "쉬운 4단계 진행",
        "guide_title": "입력하고, 고르고, 실행하고, 읽으면 끝나요.",
        "guide_1_title": "컨셉 입력",
        "guide_1_body": "제품 설명과 가격을 적어요.",
        "guide_1_detail": "상품 특징, 가격, 타깃 가설만 적으면 첫 검토가 시작돼요.",
        "guide_2_title": "패널 선택",
        "guide_2_body": "샘플 수와 조건을 골라요.",
        "guide_2_detail": "합성 페르소나 패널을 골라 어떤 사람들에게 물어볼지 정해요.",
        "guide_3_title": "비용 확인",
        "guide_3_body": "예상 호출과 비용을 확인해요.",
        "guide_3_detail": "실행 전 호출 수와 예상 비용을 먼저 보고 과한 실행을 막아요.",
        "guide_4_title": "결과 확인",
        "guide_4_body": "분포와 이유를 리포트로 받아요.",
        "guide_4_detail": "좋음, 애매함, 어려움 같은 반응 방향을 한 장 리포트처럼 읽어요.",
        "dataset_story_eyebrow": "데이터셋 이해",
        "dataset_story_title": "왜 이 데이터셋이 나왔나",
        "dataset_story_body": (
            "한국 사용자를 위한 AI는 번역만으로 부족해요. 지역, 직업, 생활 맥락, 말투가 "
            "다르기 때문에 한국 인구 분포를 닮은 합성 페르소나가 필요해졌고, "
            "이 데이터셋은 소버린 AI와 편향 완화를 목표로 공개됐어요."
        ),
        "dataset_card_1_title": "공공 분포 기반",
        "dataset_card_1_body": "KOSIS, 대법원, NHIS, KREI 등 공개 통계의 분포를 참고.",
        "dataset_card_2_title": "완전 합성",
        "dataset_card_2_body": "실제 사람 명단이 아니라 분포를 반영한 인공 페르소나.",
        "dataset_card_3_title": "패션 가설 검토",
        "dataset_card_3_body": "이 도구는 일부 페르소나를 패널처럼 뽑아 컨셉 반응을 요약.",
        "section_project": "방향성을 잡아보세요",
        "section_project_caption": (
            "아래 칸에 컨셉, 가격, 타깃 가설을 넣으면 바로 검토 준비가 돼요."
        ),
        "section_econ": "Economic Context",
        "section_econ_caption": "가격은 KOSTAT 의류비 기준으로만 맥락화해요.",
        "section_run": "Run",
        "section_run_caption": "비용 확인 후 worker thread를 시작하고 진행률을 1초마다 갱신해요.",
        "setup": "설정",
        "quick_setup_header": "쉬운 설정",
        "quick_setup_caption": "처음이면 BALANCE만 고르고 바로 진행해도 돼요.",
        "run_mode": "실행 방식",
        "mode_quick": "FAST",
        "mode_balanced": "BALANCE",
        "mode_deep": "HIGH",
        "mode_max": "MAX",
        "mode_quick_help": "50명 패널. 컨셉 초안 확인용.",
        "mode_balanced_help": "100명 패널. 기본 추천.",
        "mode_deep_help": "300명 패널. 더 넓게 확인.",
        "mode_max_help": "1000명 패널. 큰 분포 확인용.",
        "simple_summary": "{mode} · 합성 패널 {sample_size}명 · temperature {temperature}",
        "estimated_price_label": "실행 추정",
        "token_price_basis": "{sample_size}명 기준",
        "total_cost_label": "실행 1회 추정",
        "total_cost_basis": "input + output",
        "provider_label": "Provider",
        "model_label": "Model",
        "rate_unit_label": "단가 기준",
        "per_million_tokens": "USD / 1M tokens",
        "input_rate_label": "Input 단가",
        "output_rate_label": "Output 단가",
        "checked_at_label": "가격 확인일",
        "source_url_label": "가격 출처",
        "price_unset": "가격 미설정",
        "verification_label": "실호출 검증",
        "verified_provider": "검증됨",
        "unverified_provider": "미검증 provider — 실패 가능",
        "estimate_only": "참고 추정치",
        "estimate_basis_label": "추정 기준",
        "sidebar_estimate_basis": "{sample_size}명 · 짧은 제품 카드 가정",
        "run_tokens_label": "이번 실행 토큰",
        "run_cost_label": "이번 실행 추정",
        "cost_input_label": "입력 비용",
        "cost_output_label": "출력 비용",
        "cost_max_output_label": "출력 추정/상한",
        "cost_unit_note": (
            "1M token 단가는 과금 단위이고, 이번 실행은 그중 일부만 써요. "
            "실제 과금은 tokenizer, 출력 길이, 재시도, provider 계정 조건에 따라 "
            "차이가 생길 수 있어요."
        ),
        "model_compare_header": "모델별 비용 비교",
        "model_compare_caption": "현재 제품 카드 길이와 샘플 수 기준의 참고 추정치예요.",
        "cost_table_model": "Model",
        "cost_table_provider": "Provider",
        "cost_table_rate": "Input/Output 단가",
        "cost_table_estimate": "실행 추정",
        "advanced_header": "Advanced",
        "advanced_caption": "모델, 데이터, 샘플링, 필터를 직접 조정해요.",
        "advanced_enable": "세부 설정 직접 조정",
        "concept_header": "컨셉 입력",
        "input_section_basics": "기본 정보",
        "input_section_style": "스타일/착용 맥락",
        "input_section_product": "제품 디테일",
        "input_section_target": "타깃/브랜드 가설",
        "project_name": "프로젝트명",
        "category": "제품 카테고리",
        "category_placeholder": "예: 여성 니트웨어",
        "price": "가격(KRW)",
        "concept_text": "브랜드 메시지 / 제품 설명",
        "concept_placeholder": "예: 조용한 고급감의 미니멀 니트. 출근복과 주말복 겸용.",
        "fit": "핏",
        "fit_placeholder": "예: 슬림 / 레귤러 / 오버사이즈",
        "material": "소재",
        "material_placeholder": "예: 메리노 울 / 코튼 100%",
        "color": "컬러",
        "color_placeholder": "예: 차콜, 아이보리",
        "season": "시즌",
        "season_placeholder": "예: F/W, S/S, 올시즌",
        "occasion": "착용 상황",
        "occasion_placeholder": "예: 출근복, 주말 캐주얼",
        "style_tone": "스타일 톤",
        "style_tone_preset": "스타일 톤 프리셋",
        "style_tone_placeholder": "예: 미니멀, 고급감",
        "design_detail_other": "기타 디자인 디테일",
        "design_detail_other_placeholder": "예: 배색 스티치, 금속 장식",
        "price_position": "동급 브랜드 대비 가격 위치",
        "target": "타깃 가설",
        "target_placeholder": "예: 20대 후반-30대 초반 직장인 여성",
        "image_assist_toggle": "이미지 기반 컨셉 설명 보조",
        "image_assist_help": (
            "기본 OFF. 켠 경우 이미지 1장으로 설명 초안만 만들고 평가에는 확정 텍스트만 써요."
        ),
        "image_assist_upload": "컨셉 이미지 1장",
        "image_assist_upload_help": (
            "PNG, JPG, JPEG, WEBP 1장만 사용해요. 원본 이미지는 저장하지 않아요."
        ),
        "image_assist_notice": (
            "이미지는 설명 초안 생성에만 쓰고, 페르소나 평가 루프에는 반복 전송하지 않아요. "
            "민감한 출시 전 디자인은 올리지 마세요."
        ),
        "image_assist_button": "설명 초안 만들기",
        "image_assist_unavailable": (
            "이미지 분석 연결이 설정되지 않았어요. 기존 텍스트 입력으로 진행해 주세요."
        ),
        "image_assist_failed": "이미지 설명 초안 생성 실패",
        "image_assist_done": "설명 초안을 입력란에 넣었어요. 실행 전 직접 확인해 주세요.",
        "image_assist_reused": "같은 이미지의 기존 설명 초안을 다시 넣었어요.",
        "input_tab_quick": "빠른 입력",
        "input_tab_manual": "직접 입력",
        "input_tab_examples": "예시",
        "input_tab_quick_help": "컨셉을 한 덩어리로 적고 필드로 분해해 봐요.",
        "input_tab_optional": "선택 입력 — 더 정확한 결과를 원하면 추가",
        "input_tab_required_caption": "이 세 가지만 채워도 바로 실행할 수 있어요.",
        "parse_raw_label": "컨셉 한 번에 적기",
        "parse_raw_placeholder": (
            "예: 남성 셔츠, 12.9만원, 세미 오버핏, 코튼 100%, 오프화이트, 봄·가을 출근용. "
            "단정하지만 편한 데일리 셔츠."
        ),
        "parse_button": "필드로 분해",
        "parse_empty": "먼저 컨셉을 적어 주세요.",
        "parse_notice": "자동 채움 값입니다 — 확인해 주세요.",
        "parse_done": "필드로 분해했어요. 직접 입력 탭에서 확인해 주세요.",
        "parse_fallback": "자동 분해에 실패해서 설명란에만 넣었어요.",
        "preset_custom": "직접 입력",
        "preset_fit_label": "핏 프리셋",
        "preset_season_label": "시즌 프리셋",
        "preset_occasion_label": "착용 상황 프리셋",
        "preset_examples_caption": "예시를 고르면 직접 입력 탭의 필드가 채워져요.",
        "preset_example_apply": "이 예시로 채우기",
        "enter_card_title": "ENTER",
        "enter_card_subtitle": "",
        "enter_card_body": (
            "실행하면 LLM API 요청이 나가고 비용이 발생할 수 있어요. "
            "실행 전 예상 비용 확인 체크가 필요해요."
        ),
        "dataset_header": "데이터 소스",
        "source": "소스",
        "hf": "NVIDIA dataset",
        "local": "로컬 CSV/Parquet",
        "local_path": "로컬 파일 경로(data/ 하위 .csv 또는 .parquet)",
        "panel_header": "합성 패널",
        "sample_size": "샘플 수",
        "sample_help": "Advanced에서는 1명 이상 원하는 수를 직접 입력할 수 있어요.",
        "age": "연령",
        "age_min": "하한 연령",
        "age_max": "상한 연령",
        "age_min_direct": "하한 직접 입력",
        "age_max_direct": "상한 직접 입력",
        "sex": "성별",
        "sampling_seed": "sampling-seed",
        "sampling_seed_help": (
            "같은 숫자를 쓰면 같은 조건에서 같은 페르소나 샘플을 다시 뽑기 위한 재현용 값이에요."
        ),
        "province": "지역",
        "province_help": "최대 17개 시도/광역 단위를 선택할 수 있어요. 여러 개면 OR로 적용돼요.",
        "occupation": "직업 키워드",
        "occupation_help": (
            "최대 15개 대표 키워드를 선택할 수 있어요. 여러 개면 OR로 부분 검색돼요."
        ),
        "model_header": "모델",
        "model_missing": "pricing_config.yaml에 모델이 없어요.",
        "model": "모델",
        "api_key": "선택한 AI provider API KEY",
        "api_key_placeholder": "키를 붙여넣기",
        "api_key_help": "LLM API 요청용 키예요. 입력값은 화면에 표시하지 않아요.",
        "hf_token": "HF TOKEN",
        "hf_token_placeholder": "토큰을 붙여넣기",
        "hf_token_help": "Hugging Face 데이터 접근용 토큰이에요. 공개 데이터셋은 보통 없어도 돼요.",
        "kosis_header": "KOSIS 통계",
        "kosis_api_key": "KOSIS API KEY",
        "kosis_api_key_placeholder": "선택 사항",
        "kosis_api_key_help": "선택 사항이에요. KOSIS API URL 갱신에만 사용하고 저장하지 않아요.",
        "kosis_segment": "KOSIS 기준 계층",
        "kosis_segment_help": "스냅샷에서 리포트와 프롬프트에 넣을 공식 통계 기준 계층을 골라요.",
        "kosis_refresh": "KOSIS API로 통계 갱신",
        "kosis_api_url": "KOSIS statisticsData URL",
        "kosis_api_url_placeholder": "https://kosis.kr/openapi/statisticsData.do?...",
        "kosis_api_url_help": (
            "KOSIS URL 생성기로 만든 통계자료 API URL이에요. 비워두면 내장 스냅샷을 사용해요."
        ),
        "secrets_status_header": "API KEY / HF TOKEN 상태",
        "env_file_missing": ".env 파일 없음",
        "secret_present": "OK",
        "secret_missing": "MISSING",
        "openai_key_help": "OpenAI 모델 실행용 API KEY 상태예요. 값은 표시하지 않아요.",
        "anthropic_key_help": "Claude 모델 실행용 API KEY 상태예요. 값은 표시하지 않아요.",
        "google_key_help": "Gemini 모델 실행용 API KEY 상태예요. 값은 표시하지 않아요.",
        "provider_key_help": (
            "OpenAI-compatible provider 실행용 API KEY 상태예요. 값은 표시하지 않아요."
        ),
        "hf_status_help": (
            "Hugging Face 데이터셋 접근용 TOKEN 상태예요. 공개 데이터는 보통 없어도 돼요."
        ),
        "kosis_status_help": (
            "KOSIS 통계자료 API 갱신용 KEY 상태예요. 스냅샷만 쓸 때는 없어도 돼요."
        ),
        "datagokr_status_help": (
            "data.go.kr serviceKey 상태예요. 행안부 인구 통계는 키가 없으면 스냅샷을 사용해요."
        ),
        "sgis_status_help": (
            "SGIS S-Open API consumer key/secret 상태예요. 없으면 공간 통계를 건너뛰어요."
        ),
        "kma_status_help": "기상청 API허브 authKey 상태예요. 없으면 날씨 참고값을 건너뛰어요.",
        "price_context_header": "가격 맥락",
        "price_context_caption": "가격 맥락 참고 지표이며 실제 구매력을 뜻하지 않아요.",
        "cost_header": "비용 / 시간 사전 추정",
        "need_concept": "컨셉을 먼저 입력해 주세요.",
        "new_calls": "신규 호출 예상",
        "estimated_cost": "예상 비용",
        "estimated_time": "예상 시간",
        "cost_caption": "토큰과 비용은 참고 추정치예요. 가격 미설정 모델은 비용을 계산하지 않아요.",
        "debug_hash": "debug hash",
        "injection_warning": (
            "프롬프트 인젝션 의심 문구가 감지됐어요. 컨셉 문구를 다시 확인해 주세요."
        ),
        "run_confirm_header": "실행 확인",
        "cost_confirm": "참고 추정 비용·시간과 API 전송 범위를 확인했어요.",
        "injection_confirm": "감지된 문구를 확인했고 그대로 실행할게요.",
        "need_api_key": (
            "선택한 provider의 API KEY가 필요해요. "
            "입력칸에 붙여넣거나 OS 환경변수/로컬 환경 파일에 넣어둔 값을 써 주세요."
        ),
        "run_button": "ENTER",
        "run_panel_body": (
            "실행하면 선택한 AI 모델이 합성 페르소나에게 컨셉을 물어봐요. "
            "먼저 1명 preflight API 요청으로 JSON 응답을 확인하고, "
            "성공 결과는 본 실행에서 재사용해요. 패널 수만큼 비용이 발생할 수 있어요."
        ),
        "details_header": "자세히",
        "details_summary": "가격 기준, 예상 비용, 재현용 값을 확인해요.",
        "results_preview_header": "페르소나 의견 미리보기",
        "results_preview_body": (
            "대표 의견 5개만 먼저 보여줘요. 전체 결과는 엑셀용 파일로 내려받을 수 있어요."
        ),
        "dominant_preview_header": "최다 반응 대표 카드",
        "dominant_preview_body": "{sentiment} 반응이 {pct}% ({count}/{total})로 가장 높아요.",
        "dominant_preview_project": "대표 페르소나",
        "excel_download": "엑셀용 CSV 다운로드",
        "results_loading": "합성 페르소나 의견을 모으는 중이에요",
        "start_pending_title": "작동 중이에요",
        "start_pending_toast": "작업을 시작하는 중이에요. 잠시만 기다려 주세요.",
        "start_pending_body": (
            "API 연결과 첫 응답을 확인하고 있어요. 화면이 잠시 흐려져도 작업은 이어져요."
        ),
        "job_started": "작업 시작",
        "persona_preview_empty": "아직 보여줄 성공 결과가 없어요.",
        "persona_card_reasons": "좋게 본 점",
        "persona_card_concerns": "망설인 점",
        "persona_card_note": "한줄 의견",
        "status_header": "진행 상태",
        "status_help_button": "도움말",
        "status_help_title": "성공/실패 기준",
        "status_help_body": (
            "success: API 응답을 받았고 JSON 파싱과 스키마 검증을 통과한 수예요.\n\n"
            "failed: API 실패, 응답 누락, JSON 파싱 실패, "
            "필수 필드 누락 때문에 리포트 분포에 넣지 못한 수예요.\n\n"
            "cached: 같은 컨셉과 모델로 이미 저장된 결과를 다시 쓴 수예요.\n\n"
            "최종 분포와 요약에는 유효 JSON 결과만 들어가요."
        ),
        "job_missing": "현재 작업 정보를 찾을 수 없어요.",
        "refresh": "Refresh",
        "cancel": "Cancel",
        "no_results": "저장된 결과가 없어요.",
        "report_header": "리포트",
        "included": "분포 포함",
        "parse_failed": "파싱 실패",
        "api_failed": "API 실패",
        "md_download": "Markdown 다운로드",
        "csv_download": "CSV 다운로드",
        "md_preview": "Markdown 미리보기",
        "report_export_button": "리포트 내보내기",
        "report_tab_rendered": "미리보기",
        "report_tab_source": "Markdown 원문",
        "report_placeholder_title": "Markdown 리포트",
        "report_placeholder_body": "결과물이 이곳에 출력돼요.",
        "report_placeholder_hint": "ENTER 실행 후 완료되면 자동으로 이 창으로 이동해요.",
        "report_footer_disclaimer": (
            "이 결과는 합성 페르소나 기반의 pre-screening 참고용이에요. "
            "모델별 성능에 따라 문장 품질과 JSON 안정성에 차이가 생길 수 있어요. "
            "실제 조사나 사업 판단을 대체하지 않아요."
        ),
    },
    "EN": {
        "nav_brand": "k-fashion-persona",
        "nav_concept": "Concept",
        "nav_panel": "Panel",
        "nav_model": "Model",
        "nav_report": "Report",
        "subnav_title": "k-fashion-persona",
        "subnav_local": "Local run",
        "subnav_keys": "Private keys",
        "subnav_panel": "Synthetic panel",
        "subnav_run": "Run",
        "hero_title": "k-fashion-persona",
        "intro_badge": "Built by NVIDIA · grounded in Korean public-data distributions",
        "intro_title": "Use Korean synthetic personas to pre-check a fashion concept",
        "intro_body": (
            "Nemotron-Personas-Korea is a fully synthetic persona dataset developed by NVIDIA. "
            "It reflects distributions from Korean public-data sources such as KOSIS, "
            "the Supreme Court, NHIS, and KREI so Korean user context is better represented."
        ),
        "api_intro_title": "Check first: API and cost",
        "api_intro_body": (
            "When you run screening, requests go to the selected LLM provider API. "
            "The app estimates cost from input/output token prices and panel size. "
            "Actual billing follows the provider's official pricing and your account terms."
        ),
        "api_intro_1": "API keys are hidden on screen",
        "api_intro_2": "Larger panels mean more calls and cost",
        "api_intro_3": "Cost confirmation is required before running",
        "hero_main": "Read concept reaction direction before survey",
        "hero_subtext": (
            "Show a fashion concept to an AI persona panel and quickly check reaction flow "
            "before expert surveys or main research."
        ),
        "hero_eyebrow": "Local public beta · v0.8.0",
        "hero_pill_1": "Local run",
        "hero_pill_2": "No raw concept storage",
        "hero_pill_3": "Report export",
        "hero_pill_4": "🤗 nvidia/Nemotron-Personas-Korea",
        "hero_pill_5": "GitHub",
        "hero_pill_docs": "Docs",
        "hero_pill_license": "AGPL-3.0-only",
        "hero_docs_aria": "Open documentation page (docs)",
        "hero_license_aria": "Open GitHub LICENSE file",
        "cost_confirm_toast": "Check the cost/time confirmation box before running.",
        "job_already_running": (
            "A screening job is already running. Cancel it or wait for completion."
        ),
        "guide_eyebrow": "Simple 4-step flow",
        "guide_title": "Type it, choose a panel, run, then read.",
        "guide_1_title": "Describe",
        "guide_1_body": "Enter concept and price.",
        "guide_1_detail": "Start with the product idea, price, and target hypothesis.",
        "guide_2_title": "Choose panel",
        "guide_2_body": "Set sample size and filters.",
        "guide_2_detail": "Pick which synthetic personas should react to the concept.",
        "guide_3_title": "Check cost",
        "guide_3_body": "Review calls and estimate.",
        "guide_3_detail": "See expected calls and cost before any paid run.",
        "guide_4_title": "Read report",
        "guide_4_body": "Export response patterns.",
        "guide_4_detail": "Read the direction of responses as a compact report.",
        "dataset_story_eyebrow": "Dataset context",
        "dataset_story_title": "Why this dataset exists",
        "dataset_story_body": (
            "AI for Korean users needs more than translation. Region, occupation, lifestyle, "
            "and communication norms matter. This dataset was released to support sovereign AI, "
            "reduce missing context, and mitigate bias in synthetic persona data."
        ),
        "dataset_card_1_title": "Public distributions",
        "dataset_card_1_body": "Uses distributions from KOSIS, Supreme Court, NHIS, and KREI.",
        "dataset_card_2_title": "Fully synthetic",
        "dataset_card_2_body": "Not a list of real people; personas mirror statistical patterns.",
        "dataset_card_3_title": "Fashion hypothesis check",
        "dataset_card_3_body": (
            "This tool samples personas as a panel and summarizes concept reactions."
        ),
        "section_project": "Shape the direction",
        "section_project_caption": (
            "Enter concept, price, and target hypothesis below to prepare a run."
        ),
        "section_econ": "Economic Context",
        "section_econ_caption": "Price is contextualized only against KOSTAT clothing spend.",
        "section_run": "Run",
        "section_run_caption": (
            "Start a worker thread after cost confirmation and poll progress every second."
        ),
        "setup": "Setup",
        "quick_setup_header": "Quick setup",
        "quick_setup_caption": "For a first run, choose BALANCE and continue.",
        "run_mode": "Run mode",
        "mode_quick": "FAST",
        "mode_balanced": "BALANCE",
        "mode_deep": "HIGH",
        "mode_max": "MAX",
        "mode_quick_help": "50-person panel for rough drafts.",
        "mode_balanced_help": "100-person panel. Recommended default.",
        "mode_deep_help": "300-person panel for broader signal.",
        "mode_max_help": "1000-person panel for large distribution checks.",
        "simple_summary": "{mode} · {sample_size} synthetic personas · temperature {temperature}",
        "estimated_price_label": "Run estimate",
        "token_price_basis": "{sample_size} personas",
        "total_cost_label": "One-run estimate",
        "total_cost_basis": "input + output",
        "provider_label": "Provider",
        "model_label": "Model",
        "rate_unit_label": "Rate unit",
        "per_million_tokens": "USD / 1M tokens",
        "input_rate_label": "Input rate",
        "output_rate_label": "Output rate",
        "checked_at_label": "Price checked",
        "source_url_label": "Price source",
        "price_unset": "Price unset",
        "verification_label": "Live-call verification",
        "verified_provider": "Verified",
        "unverified_provider": "Unverified provider — calls may fail",
        "estimate_only": "Reference estimate",
        "estimate_basis_label": "Estimate basis",
        "sidebar_estimate_basis": "{sample_size} personas · short product card",
        "run_tokens_label": "Run tokens",
        "run_cost_label": "Run estimate",
        "cost_input_label": "Input cost",
        "cost_output_label": "Output cost",
        "cost_max_output_label": "Output estimate / cap",
        "cost_unit_note": (
            "The 1M-token price is the billing rate unit; this run uses only a portion of it. "
            "Actual billing can vary by tokenizer, output length, retries, and provider "
            "account terms."
        ),
        "model_compare_header": "Model Cost Comparison",
        "model_compare_caption": (
            "Reference one-run estimate for the current product-card length and sample size."
        ),
        "cost_table_model": "Model",
        "cost_table_provider": "Provider",
        "cost_table_rate": "Input/output rate",
        "cost_table_estimate": "Run estimate",
        "advanced_header": "Advanced",
        "advanced_caption": "Directly control model, data source, sampling, and filters.",
        "advanced_enable": "Customize advanced settings",
        "concept_header": "Concept",
        "input_section_basics": "Basics",
        "input_section_style": "Style and Wearing Context",
        "input_section_product": "Product Details",
        "input_section_target": "Target and Brand Hypothesis",
        "project_name": "Project name",
        "category": "Product category",
        "category_placeholder": "e.g. women's knitwear",
        "price": "Price (KRW)",
        "concept_text": "Brand message / product description",
        "concept_placeholder": "e.g. minimal knitwear for weekday office and weekend wear.",
        "fit": "Fit",
        "fit_placeholder": "e.g. slim / regular / oversize",
        "material": "Material",
        "material_placeholder": "e.g. merino wool / 100% cotton",
        "color": "Color",
        "color_placeholder": "e.g. charcoal, ivory",
        "season": "Season",
        "season_placeholder": "e.g. F/W, S/S, all-season",
        "occasion": "Occasion",
        "occasion_placeholder": "e.g. office, weekend casual",
        "style_tone": "Style tone",
        "style_tone_preset": "Style tone preset",
        "style_tone_placeholder": "e.g. minimal, refined",
        "design_detail_other": "Other design details",
        "design_detail_other_placeholder": "e.g. contrast stitching, metal detail",
        "price_position": "Price position vs. peer brands",
        "target": "Target hypothesis",
        "target_placeholder": "e.g. women in their late 20s to early 30s",
        "image_assist_toggle": "Image-based concept description assist",
        "image_assist_help": (
            "Default OFF. When enabled, one image can draft description text; only confirmed "
            "text is used for screening."
        ),
        "image_assist_upload": "One concept image",
        "image_assist_upload_help": "PNG, JPG, JPEG, or WEBP. The original image is not stored.",
        "image_assist_notice": (
            "The image is used only to draft text and is not resent through the persona loop. "
            "Do not upload sensitive pre-launch designs."
        ),
        "image_assist_button": "Draft description",
        "image_assist_unavailable": "Image analysis is not configured. Continue with text input.",
        "image_assist_failed": "Image draft failed",
        "image_assist_done": "Draft text was placed in the input. Review it before running.",
        "image_assist_reused": "Reused the existing draft for the same image.",
        "input_tab_quick": "Quick input",
        "input_tab_manual": "Manual input",
        "input_tab_examples": "Examples",
        "input_tab_quick_help": "Write the concept in one block and split it into fields.",
        "input_tab_optional": "Optional input — add more for sharper results",
        "input_tab_required_caption": "Just these three are enough to run.",
        "parse_raw_label": "Write the whole concept",
        "parse_raw_placeholder": (
            "e.g. men's shirt, 129,000 KRW, semi-oversize, 100% cotton, off-white, "
            "spring/fall office wear. Tidy but comfortable daily shirt."
        ),
        "parse_button": "Split into fields",
        "parse_empty": "Write the concept first.",
        "parse_notice": "Auto-filled values — please review.",
        "parse_done": "Split into fields. Review them in the Manual input tab.",
        "parse_fallback": "Auto-split failed, so only the description was filled.",
        "preset_custom": "Custom",
        "preset_fit_label": "Fit preset",
        "preset_season_label": "Season preset",
        "preset_occasion_label": "Occasion preset",
        "preset_examples_caption": "Pick an example to fill the Manual input fields.",
        "preset_example_apply": "Fill with this example",
        "enter_card_title": "ENTER",
        "enter_card_subtitle": "",
        "enter_card_body": (
            "Running can send LLM API requests and incur cost. "
            "Cost confirmation is required before running."
        ),
        "dataset_header": "Data source",
        "source": "Source",
        "hf": "NVIDIA dataset",
        "local": "Local CSV/Parquet",
        "local_path": "Local file path under data/ (.csv or .parquet)",
        "panel_header": "Synthetic panel",
        "sample_size": "Sample size",
        "sample_help": "Advanced accepts any sample size of 1 or more.",
        "age": "Age",
        "age_min": "Minimum age",
        "age_max": "Maximum age",
        "age_min_direct": "Minimum age direct input",
        "age_max_direct": "Maximum age direct input",
        "sex": "Sex",
        "sampling_seed": "sampling-seed",
        "sampling_seed_help": (
            "A reproducibility value. Reusing the same number keeps sampling stable "
            "under the same conditions."
        ),
        "province": "Region",
        "province_help": "Select up to 17 province/city units. Multiple choices are OR filters.",
        "occupation": "Occupation keyword",
        "occupation_help": (
            "Select up to 15 representative keywords. Multiple choices are OR partial matches."
        ),
        "model_header": "Model",
        "model_missing": "No models in pricing_config.yaml.",
        "model": "Model",
        "api_key": "Selected AI provider API KEY",
        "api_key_placeholder": "Paste key",
        "api_key_help": "Used for LLM API requests. Typed values are hidden on screen.",
        "hf_token": "HF TOKEN",
        "hf_token_placeholder": "Paste token",
        "hf_token_help": (
            "Used for Hugging Face data access. Public datasets usually do not need it."
        ),
        "kosis_header": "KOSIS statistics",
        "kosis_api_key": "KOSIS API KEY",
        "kosis_api_key_placeholder": "Optional",
        "kosis_api_key_help": "Optional. Used only for KOSIS API URL refresh and not stored.",
        "kosis_segment": "KOSIS reference segment",
        "kosis_segment_help": (
            "Choose the official-statistics segment inserted into prompts and reports."
        ),
        "kosis_refresh": "Refresh stats from KOSIS API",
        "kosis_api_url": "KOSIS statisticsData URL",
        "kosis_api_url_placeholder": "https://kosis.kr/openapi/statisticsData.do?...",
        "kosis_api_url_help": (
            "URL generated by the KOSIS statisticsData URL builder. "
            "Leave blank to use the committed snapshot."
        ),
        "secrets_status_header": "API KEY / HF TOKEN status",
        "env_file_missing": ".env file not found",
        "secret_present": "OK",
        "secret_missing": "MISSING",
        "openai_key_help": "OpenAI API KEY status for model calls. Values are never shown.",
        "anthropic_key_help": "Claude API KEY status for model calls. Values are never shown.",
        "google_key_help": "Gemini API KEY status for model calls. Values are never shown.",
        "provider_key_help": (
            "API KEY status for OpenAI-compatible provider calls. Values are never shown."
        ),
        "hf_status_help": (
            "HF TOKEN status for Hugging Face data access. Public data usually works without it."
        ),
        "kosis_status_help": (
            "KOSIS statisticsData API key status. Not needed when using the snapshot only."
        ),
        "datagokr_status_help": (
            "data.go.kr serviceKey status. MOIS population context falls back to the snapshot."
        ),
        "sgis_status_help": (
            "SGIS S-Open API consumer key/secret status. Spatial context is skipped without it."
        ),
        "kma_status_help": "KMA API Hub authKey status. Weather context is skipped without it.",
        "price_context_header": "Price context",
        "price_context_caption": "This is context only, not real purchasing power.",
        "cost_header": "Cost / time estimate",
        "need_concept": "Enter a concept first.",
        "new_calls": "New calls",
        "estimated_cost": "Estimated cost",
        "estimated_time": "Estimated time",
        "cost_caption": (
            "Token and cost values are reference estimates. Models without prices are not costed."
        ),
        "debug_hash": "debug hash",
        "injection_warning": (
            "Possible prompt-injection text detected. Review the concept before running."
        ),
        "run_confirm_header": "Run confirmation",
        "cost_confirm": "I reviewed the reference cost/time estimate and API transfer scope.",
        "injection_confirm": "I reviewed the detected text and want to run anyway.",
        "need_api_key": (
            "The selected provider needs an API KEY. "
            "Paste one here or use one set in your OS environment or local env file."
        ),
        "run_button": "ENTER",
        "run_panel_body": (
            "Running asks the selected AI model to evaluate the concept through synthetic "
            "personas. It first sends one preflight API request to validate JSON, then reuses "
            "that successful result in the main run. Cost can increase with panel size."
        ),
        "details_header": "Details",
        "details_summary": "Check price context, cost estimate, and reproducibility values.",
        "results_preview_header": "Persona opinion preview",
        "results_preview_body": (
            "Shows 5 representative opinions first. Download the full data for Excel."
        ),
        "dominant_preview_header": "Top-response representative card",
        "dominant_preview_body": "{sentiment} responses are highest at {pct}% ({count}/{total}).",
        "dominant_preview_project": "Representative persona",
        "excel_download": "Download CSV for Excel",
        "results_loading": "Collecting synthetic persona opinions",
        "start_pending_title": "Working",
        "start_pending_toast": "Starting the run. Please wait a moment.",
        "start_pending_body": (
            "Checking the API connection and first response. "
            "Work continues even if the screen looks dim for a moment."
        ),
        "job_started": "Job started",
        "persona_preview_empty": "No successful opinion rows to preview yet.",
        "persona_card_reasons": "Reasons",
        "persona_card_concerns": "Concerns",
        "persona_card_note": "Note",
        "status_header": "Progress",
        "status_help_button": "Help",
        "status_help_title": "Success/failure criteria",
        "status_help_body": (
            "success: API response was received and passed JSON parsing plus schema validation.\n\n"
            "failed: API failure, missing response, JSON parsing failure, or missing "
            "required fields kept the row out of the report distribution.\n\n"
            "cached: A stored result for the same concept and model was reused.\n\n"
            "Only valid JSON results are included in the final distribution and summary."
        ),
        "job_missing": "Current job record was not found.",
        "refresh": "Refresh",
        "cancel": "Cancel",
        "no_results": "No saved results yet.",
        "report_header": "Report",
        "included": "Included",
        "parse_failed": "Parse failed",
        "api_failed": "API failed",
        "md_download": "Download Markdown",
        "csv_download": "Download CSV",
        "md_preview": "Markdown preview",
        "report_export_button": "Export report",
        "report_tab_rendered": "Preview",
        "report_tab_source": "Markdown source",
        "report_placeholder_title": "Markdown report",
        "report_placeholder_body": "Results will appear here.",
        "report_placeholder_hint": "After ENTER completes, the page scrolls to this panel.",
        "report_footer_disclaimer": (
            "This result is reference-only pre-screening based on synthetic personas. "
            "Model behavior and JSON stability can vary by provider. "
            "It does not replace real research or business decisions."
        ),
    },
}
