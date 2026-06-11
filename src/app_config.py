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
