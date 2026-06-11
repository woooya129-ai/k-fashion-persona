# SPDX-License-Identifier: AGPL-3.0-only
"""Shared app constants for Streamlit wiring, UI, and orchestration."""

from __future__ import annotations

from typing import Any

PRODUCT_CARD_EMPTY_PLACEHOLDER = "미입력"
PRODUCT_CARD_FIELD_ORDER: tuple[str, ...] = (
    "category",
    "price",
    "fit",
    "material",
    "color",
    "design_details",
    "season",
    "occasion",
    "style_tone",
    "target_hypothesis",
    "description",
)
PRODUCT_CARD_FIELD_LABELS_KR: dict[str, str] = {
    "category": "카테고리",
    "price": "가격",
    "fit": "핏",
    "material": "소재",
    "color": "컬러",
    "design_details": "디자인 디테일",
    "season": "시즌",
    "occasion": "착용 상황",
    "style_tone": "스타일 톤",
    "target_hypothesis": "타깃 가설",
    "description": "브랜드 메시지/제품 설명",
}

DESIGN_DETAIL_OPTIONS: tuple[str, ...] = (
    "그래픽 있음",
    "패턴 있음",
    "로고 있음",
    "자수 있음",
    "프린트 있음",
    "워싱/가공 있음",
    "장식 없음",
)
STYLE_TONE_PRESETS: tuple[str, ...] = (
    "직접 입력",
    "미니멀",
    "정돈된 클래식",
    "캐주얼",
    "스트릿",
    "스포티",
    "페미닌",
    "워크웨어",
    "고급감",
)
PRICE_POSITION_OPTIONS: tuple[str, ...] = (
    "모르겠음",
    "저렴한 편",
    "비슷한 편",
    "비싼 편",
)

# Stream B (input-UI) preset selectors. "직접 입력" keeps a free-text fallback,
# mirroring STYLE_TONE_PRESETS.
FIT_PRESETS: tuple[str, ...] = (
    "직접 입력",
    "슬림",
    "레귤러",
    "세미오버",
    "오버",
)
SEASON_PRESETS: tuple[str, ...] = (
    "봄·가을",
    "여름",
    "겨울",
    "사계절",
)
OCCASION_PRESETS: tuple[str, ...] = (
    "출근",
    "데일리",
    "모임",
    "운동",
    "행사",
)

# Whitelist of session-state keys that the 빠른 입력/예시 tabs may write into.
# Keeping this explicit prevents 자동 채움 from clobbering unrelated widgets.
CONCEPT_AUTOFILL_STATE_KEYS: tuple[str, ...] = (
    "kfps_product_category",
    "kfps_fit",
    "kfps_material",
    "kfps_color",
    "kfps_season",
    "kfps_occasion",
    "kfps_style_tone",
    "kfps_target_hypothesis",
    "kfps_concept_description",
)

# Ready-made concept cards rendered in the 예시 tab. Each maps directly onto the
# autofill whitelist above (plus a label/summary for display).
CONCEPT_EXAMPLE_PRESETS: dict[str, dict[str, Any]] = {
    "office_shirt": {
        "label": "출근 셔츠",
        "summary": "남성 셔츠 · 129,000원 · 세미 오버핏 · 코튼 100% · 오프화이트",
        "values": {
            "kfps_product_category": "남성 셔츠",
            "kfps_fit": "세미 오버핏",
            "kfps_material": "코튼 100%",
            "kfps_color": "오프화이트",
            "kfps_season": "봄·가을",
            "kfps_occasion": "출근, 미팅",
            "kfps_style_tone": "정돈된 클래식",
            "kfps_target_hypothesis": "실용성과 관리 편의성을 보는 직장인",
            "kfps_concept_description": (
                "구김을 줄인 코튼 셔츠. 단정한 인상과 편한 움직임을 함께 고려한 데일리 출근 아이템."
            ),
        },
    },
    "weekend_knit": {
        "label": "주말 니트",
        "summary": "여성 니트 · 89,000원 · 레귤러 핏 · 메리노 울 · 아이보리",
        "values": {
            "kfps_product_category": "여성 니트",
            "kfps_fit": "레귤러",
            "kfps_material": "메리노 울 70%",
            "kfps_color": "아이보리",
            "kfps_season": "겨울",
            "kfps_occasion": "데일리, 모임",
            "kfps_style_tone": "미니멀",
            "kfps_target_hypothesis": "조용한 고급감을 선호하는 20~30대 여성",
            "kfps_concept_description": (
                "부드러운 메리노 울 니트. 출근복과 주말복을 가볍게 오가는 데일리 아이템."
            ),
        },
    },
    "active_top": {
        "label": "운동 탑",
        "summary": "공용 액티브웨어 · 49,000원 · 슬림 핏 · 기능성 폴리 · 블랙",
        "values": {
            "kfps_product_category": "공용 액티브웨어 탑",
            "kfps_fit": "슬림",
            "kfps_material": "기능성 폴리에스터",
            "kfps_color": "블랙",
            "kfps_season": "사계절",
            "kfps_occasion": "운동, 데일리",
            "kfps_style_tone": "스포티",
            "kfps_target_hypothesis": "가성비와 활동성을 중시하는 20~30대",
            "kfps_concept_description": (
                "땀 배출이 빠른 기능성 소재의 액티브 탑. 운동과 일상에서 두루 입기 좋은 베이직."
            ),
        },
    },
}

APP_VERSION = "0.8.0"
DEFAULT_PRICE_CONTEXT_VERSION = "kosis_hybrid_2026_v1"
DEFAULT_TEMPERATURE = 0.3
MAX_SAMPLE_SIZE = 1_000
DEFAULT_HF_MAX_SCAN_ROWS = 3_000
TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
ESTIMATE_SYSTEM_PROMPT_TOKENS = 400
ESTIMATE_PERSONA_TOKENS = 350
ESTIMATE_SIDEBAR_CONCEPT_TOKENS = 160
ESTIMATE_ECONOMIC_CONTEXT_TOKENS = 180
ESTIMATE_SCHEMA_INSTRUCTION_TOKENS = 120
ESTIMATE_OUTPUT_TOKENS_PER_PERSONA = 325
MAX_OUTPUT_TOKENS_PER_PERSONA = 1200
RUN_MODE_PRESETS: dict[str, dict[str, Any]] = {
    "preview": {"sample_size": 5, "temperature": 0.2},
    "quick": {"sample_size": 50, "temperature": 0.2},
    "balanced": {"sample_size": 100, "temperature": 0.3},
    "deep": {"sample_size": 300, "temperature": 0.3},
    "max": {"sample_size": MAX_SAMPLE_SIZE, "temperature": 0.3},
}
KOREA_PROVINCE_OPTIONS: tuple[str, ...] = (
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
)
OCCUPATION_KEYWORD_OPTIONS: tuple[str, ...] = (
    "사무",
    "전문",
    "관리",
    "서비스",
    "판매",
    "자영",
    "학생",
    "주부",
    "교육",
    "의료",
    "기술",
    "생산",
    "운전",
    "농림어업",
    "예술",
)
BEGINNER_MODEL_PRIORITY: tuple[str, ...] = (
    "gpt-5.5",
    "gpt-4o-mini",
    "gpt-5-mini",
    "gpt-5-nano",
    "gemini-2.5-flash-lite",
    "claude-haiku-4-5",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "gpt-5.2",
    "gpt-4o",
)
