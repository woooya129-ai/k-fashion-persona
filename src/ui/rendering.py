# SPDX-License-Identifier: AGPL-3.0-only
"""Streamlit rendering helpers for k-fashion-persona."""

from __future__ import annotations

import csv
import html
import io
import json
import logging
import os
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from pydantic import ValidationError

from src import secrets_loader
from src.app_config import (
    BEGINNER_MODEL_PRIORITY,
    DEFAULT_PRICE_CONTEXT_VERSION,
    DEFAULT_TEMPERATURE,
    ESTIMATE_ECONOMIC_CONTEXT_TOKENS,
    ESTIMATE_OUTPUT_TOKENS_PER_PERSONA,
    ESTIMATE_PERSONA_TOKENS,
    ESTIMATE_SCHEMA_INSTRUCTION_TOKENS,
    ESTIMATE_SIDEBAR_CONCEPT_TOKENS,
    ESTIMATE_SYSTEM_PROMPT_TOKENS,
    KOREA_PROVINCE_OPTIONS,
    MAX_OUTPUT_TOKENS_PER_PERSONA,
    MAX_SAMPLE_SIZE,
    OCCUPATION_KEYWORD_OPTIONS,
    PRODUCT_CARD_EMPTY_PLACEHOLDER,
    PRODUCT_CARD_FIELD_LABELS_KR,
    PRODUCT_CARD_FIELD_ORDER,
    RUN_MODE_PRESETS,
)
from src.cache import compute_concept_hash, compute_price_context_hash, normalize_concept_text
from src.cost_estimator import (
    DEFAULT_CONCURRENCY,
    CostEstimate,
    TokenEstimate,
    count_tokens_approx,
    estimate_cost,
    estimate_tokens,
)
from src.data_loader import DEFAULT_HF_DATASET_ID, DEFAULT_SPLIT
from src.economic_context import (
    DEFAULT_REFERENCE_SEGMENT_ID,
    DEFAULT_REFERENCE_SEGMENT_LABEL,
    KOSIS_STATISTICS_URL_VAR,
    KOSTAT_2025_ANNUAL_CLOTHING_KRW,
    build_price_context,
    kosis_segment_options,
)
from src.persona_filter import PersonaFilter
from src.pricing_config import ModelPricing, get_model_pricing
from src.result_parser import EvaluationResult, validate_evaluation_payload
from src.ui.assets import (
    DIRECTION_BG_PATH,
    FABRIC_PATH,
    GITHUB_PILL_ICON_HTML,
    HF_DATASET_URL,
    PUBLIC_GITHUB_LICENSE_URL,
    PUBLIC_GITHUB_REPO_URL,
    _image_data_uri,
    docs_page_url,
)
from src.ui.copy import UI_COPY
from src.ui.dynamic_css import build_comfort_ui_css

logger = logging.getLogger(__name__)
ResultRow = dict[str, Any]


def _safe_provider_key(
    provider: str,
    override_key: str,
    api_key_env: str | None = None,
) -> str | None:

    if override_key.strip():
        return override_key.strip()

    try:
        return secrets_loader.get_provider_key(provider, api_key_env=api_key_env)
    except TypeError:
        return secrets_loader.get_provider_key(provider)
    except ValueError:
        return None


def _provider_key_policy_notice(lang: str) -> str | None:
    if not secrets_loader.require_user_provider_key():
        return None

    if lang == "EN":
        return (
            "This public HF Space does not use a shared owner LLM API key. "
            "Enter your own provider API key for this session. The app does not save it."
        )

    return (
        "이 공개 HF Space는 운영자 공용 LLM API key를 사용하지 않아. "
        "방문자 본인의 provider API key를 이번 세션에 직접 입력해서 써야 해. "
        "앱은 입력값을 저장하지 않아."
    )


def _default_model_alias(model_options: list[str]) -> str:

    for preferred in BEGINNER_MODEL_PRIORITY:
        for option in model_options:
            if preferred in option:
                return option

    return model_options[0]


def _model_version_sort(alias: str) -> tuple[int, ...]:

    return tuple(-int(token) for token in alias.replace(".", "-").split("-") if token.isdigit())


def _model_sort_key(alias: str) -> tuple[str, int, tuple[int, ...], str]:

    lower = alias.lower()

    if lower.startswith("claude-"):
        claude_family_order = {"haiku": 0, "sonnet": 1, "opus": 2}

        for family, rank in claude_family_order.items():
            if f"claude-{family}" in lower:
                return ("claude", rank, _model_version_sort(lower), lower)

        return ("claude", 99, _model_version_sort(lower), lower)

    return (lower, 0, _model_version_sort(lower), lower)


def _provider_display_name(provider: str, api_key_env: str | None = None) -> str:
    if provider == "openai_compatible" and api_key_env:
        prefix = api_key_env.removesuffix("_API_KEY")
        provider_names = {
            "GROQ": "Groq",
            "DEEPSEEK": "DeepSeek",
            "QWEN": "Qwen",
        }
        return provider_names.get(prefix, prefix.replace("_", " ").title())
    return {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "openai_compatible": "OpenAI-compatible",
    }.get(provider, provider)


def _model_option_label(alias: str, pricing_config: dict[str, ModelPricing]) -> str:
    pricing = pricing_config[alias]
    provider_label = _provider_display_name(pricing.provider, pricing.api_key_env)
    return f"{provider_label} / {alias}"


def _sorted_model_options(pricing_config: dict[str, ModelPricing]) -> list[str]:

    return sorted(pricing_config.keys(), key=_model_sort_key)


def _run_mode_label(lang: str, mode_key: str) -> str:

    return ui_text(lang, f"mode_{mode_key}")


def ui_text(lang: str, key: str) -> str:

    return UI_COPY.get(lang, UI_COPY["KR"]).get(key, UI_COPY["KR"].get(key, key))


def _current_ui_state() -> tuple[str, str]:

    if "kfps_lang_is_kor" not in st.session_state:
        if "kfps_lang_is_en" in st.session_state:
            st.session_state["kfps_lang_is_kor"] = not bool(st.session_state["kfps_lang_is_en"])

        else:
            st.session_state["kfps_lang_is_kor"] = (
                st.session_state.get("kfps_language", "KR") == "KR"
            )

    if "kfps_theme_is_dark" not in st.session_state:
        st.session_state["kfps_theme_is_dark"] = st.session_state.get("kfps_theme") in {
            "Dark",
            "dark",
        }

    lang = "KR" if bool(st.session_state.get("kfps_lang_is_kor")) else "EN"

    theme = "dark" if bool(st.session_state.get("kfps_theme_is_dark")) else "light"

    return lang, theme


def apply_design_system(dark_mode: bool) -> None:

    st.html(
        build_comfort_ui_css(
            dark_mode,
            fabric_uri=_image_data_uri(FABRIC_PATH),
            direction_uri=_image_data_uri(DIRECTION_BG_PATH),
        )
    )


def render_top_bar(lang_seed: str, theme_seed: str) -> tuple[str, bool]:

    product_name = html.escape(ui_text(lang_seed, "hero_title"))

    with st.container(key="kfps_top_bar"):
        if "kfps_sidebar_hidden" not in st.session_state:
            st.session_state["kfps_sidebar_hidden"] = False

        if st.button(" ", key="kfps_sidebar_toggle_button"):
            st.session_state["kfps_sidebar_hidden"] = not bool(
                st.session_state.get("kfps_sidebar_hidden")
            )

            st.rerun()

        state_class = "kfps-sidebar-hidden" if st.session_state.get("kfps_sidebar_hidden") else ""

        st.html(f'<span class="kfps-sidebar-state {state_class}" aria-hidden="true"></span>')

        st.html(
            f"""

            <div class="kfps-top-brandbar" aria-label="Product">

              <strong>{product_name}</strong>

            </div>

            <div class="kfps-top-toggle-labels" aria-hidden="true">

              <span>ENG</span>

              <span></span>

              <span>KOR</span>

              <b>/</b>

              <span>LIGHT</span>

              <span></span>

              <span>DARK</span>

            </div>

            """
        )

        lang_is_kor = st.toggle(
            "Language",
            key="kfps_lang_is_kor",
            label_visibility="collapsed",
            width="content",
        )

        theme_is_dark = st.toggle(
            "Theme",
            key="kfps_theme_is_dark",
            label_visibility="collapsed",
            width="content",
        )

    return ("KR" if lang_is_kor else "EN"), bool(theme_is_dark)


def render_secret_field_header(label: str, present: bool, help_text: str) -> None:

    state_class = "ok" if present else "missing"

    mark = "O" if present else "X"

    st.html(
        f"""

        <div class="kfps-secret-field-head">

          <span class="kfps-key-name">{html.escape(label)}</span>

          <span class="kfps-secret-field-actions">

            <span class="kfps-key-mark {state_class}" aria-label="{mark}">{mark}</span>

            <span class="material-symbols-rounded kfps-help-dot kfps-secret-help-icon"

                  data-tooltip="{html.escape(help_text, quote=True)}"

                  aria-label="{html.escape(help_text, quote=True)}" tabindex="0">help</span>

          </span>

        </div>

        """
    )


def render_secret_password_input(
    label: str,
    *,
    placeholder: str,
    key: str,
    present: bool,
    help_text: str,
) -> str:

    render_secret_field_header(label, present, help_text)

    return st.text_input(
        label,
        placeholder=placeholder,
        type="password",
        key=key,
        label_visibility="collapsed",
    )


def render_enter_card(lang: str) -> None:

    title = html.escape(ui_text(lang, "enter_card_title"))

    subtitle_raw = ui_text(lang, "enter_card_subtitle").strip()

    subtitle_html = (
        f'<span class="kfps-enter-subtitle">{html.escape(subtitle_raw)}</span>'
        if subtitle_raw
        else ""
    )

    body = html.escape(ui_text(lang, "enter_card_body"))

    st.html(
        f"""

        <div class="kfps-enter-card" role="note" aria-label="{title}">

          <div class="kfps-enter-top">

            <span class="material-symbols-rounded kfps-enter-arrow"

                  aria-hidden="true">keyboard_return</span>

            <span class="kfps-enter-title-stack">

              <strong>{title}</strong>

              {subtitle_html}

            </span>

          </div>

          <span class="kfps-enter-warning">

            <span class="material-symbols-rounded kfps-enter-warning-icon"

                  aria-hidden="true">warning</span>

            <span>{body}</span>

          </span>

        </div>

        """
    )


def render_inline_note(message: str, *, extra_class: str = "") -> None:

    class_name = "kfps-inline-note"

    if extra_class:
        class_name += f" {html.escape(extra_class, quote=True)}"

    st.html(f'<div class="{class_name}">{html.escape(message)}</div>')


def render_input_section_heading(title: str) -> None:

    st.html(
        f"""

        <div class="kfps-input-section-title" role="heading" aria-level="4">

          {html.escape(title)}

        </div>

        """
    )


def _estimate_run_tokens(sample_size: int, concept_tokens: int) -> TokenEstimate:

    return estimate_tokens(
        system_prompt_tokens=ESTIMATE_SYSTEM_PROMPT_TOKENS,
        persona_tokens=ESTIMATE_PERSONA_TOKENS,
        concept_tokens=max(0, int(concept_tokens)),
        economic_context_tokens=ESTIMATE_ECONOMIC_CONTEXT_TOKENS,
        schema_instruction_tokens=ESTIMATE_SCHEMA_INSTRUCTION_TOKENS,
        expected_output_tokens_per_persona=ESTIMATE_OUTPUT_TOKENS_PER_PERSONA,
        new_call_count=max(0, int(sample_size)),
        cached_count=0,
    )


def _estimate_model_cost(token_est: TokenEstimate, pricing: ModelPricing) -> CostEstimate | None:

    if pricing.input_per_million_usd is None or pricing.output_per_million_usd is None:
        return None

    return estimate_cost(
        token_est,
        pricing.input_per_million_usd,
        pricing.output_per_million_usd,
        concurrency=DEFAULT_CONCURRENCY,
    )


def _estimate_sidebar_cost(
    sample_size: int, pricing: ModelPricing
) -> tuple[TokenEstimate, CostEstimate | None]:

    token_est = _estimate_run_tokens(sample_size, ESTIMATE_SIDEBAR_CONCEPT_TOKENS)

    cost_est = _estimate_model_cost(token_est, pricing)

    return token_est, cost_est


def _format_tokens(tokens: int) -> str:

    if tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"

    return str(tokens)


def _format_usd(value: float) -> str:

    if value < 0.01:
        return f"${value:.4f}"

    return f"${value:.2f}"


def _format_price(value: float | None, lang: str) -> str:
    if value is None:
        return ui_text(lang, "price_unset")
    return _format_usd(value)


def _format_cost_range(cost_est: CostEstimate) -> str:

    return (
        f"{_format_usd(cost_est.estimated_cost_usd_low)} - "
        f"{_format_usd(cost_est.estimated_cost_usd_high)}"
    )


def _input_cost_usd(token_est: TokenEstimate, pricing: ModelPricing) -> float:

    if pricing.input_per_million_usd is None:
        return 0.0

    return token_est.estimated_input_tokens_total / 1_000_000 * pricing.input_per_million_usd


def _output_cost_usd(token_est: TokenEstimate, pricing: ModelPricing) -> float:

    if pricing.output_per_million_usd is None:
        return 0.0

    return token_est.estimated_output_tokens_total / 1_000_000 * pricing.output_per_million_usd


def render_model_metadata(
    pricing: ModelPricing,
    model_name: str,
    *,
    sample_size: int | None = None,
    lang: str = "KR",
) -> None:

    rows: list[tuple[str, str]] = [
        (
            ui_text(lang, "provider_label"),
            _provider_display_name(pricing.provider, pricing.api_key_env),
        ),
        (ui_text(lang, "model_label"), model_name),
        (ui_text(lang, "rate_unit_label"), ui_text(lang, "per_million_tokens")),
        (ui_text(lang, "input_rate_label"), _format_price(pricing.input_per_million_usd, lang)),
        (ui_text(lang, "output_rate_label"), _format_price(pricing.output_per_million_usd, lang)),
        (
            ui_text(lang, "verification_label"),
            ui_text(
                lang,
                (
                    "verified_provider"
                    if getattr(pricing, "verified", True)
                    else "unverified_provider"
                ),
            ),
        ),
    ]
    if pricing.checked_at:
        rows.append((ui_text(lang, "checked_at_label"), pricing.checked_at))
    if pricing.source_url:
        rows.append((ui_text(lang, "source_url_label"), pricing.source_url))

    if sample_size is not None:
        token_est, cost_est = _estimate_sidebar_cost(sample_size, pricing)

        rows.extend(
            [
                (
                    ui_text(lang, "estimate_basis_label"),
                    ui_text(lang, "sidebar_estimate_basis").format(sample_size=sample_size),
                ),
                (
                    ui_text(lang, "run_tokens_label"),
                    (
                        f"{_format_tokens(token_est.estimated_input_tokens_total)} input / "
                        f"{_format_tokens(token_est.estimated_output_tokens_total)} output"
                    ),
                ),
                (
                    ui_text(lang, "total_cost_label"),
                    _format_cost_range(cost_est) if cost_est else ui_text(lang, "price_unset"),
                ),
            ]
        )

    row_html = "".join(
        '<div class="kfps-model-meta-row">'
        f'<span class="kfps-model-meta-label">{html.escape(label)}</span>'
        f'<span class="kfps-model-meta-value">{html.escape(value)}</span>'
        "</div>"
        for label, value in rows
    )

    st.html(f'<div class="kfps-model-meta">{row_html}</div>')
    if not getattr(pricing, "verified", True):
        st.warning(ui_text(lang, "unverified_provider"))


def nav_link_pills_html(lang: str, *, footer: bool = False) -> str:
    """Hero + footer: dataset, GitHub, Docs (same order as static landing)."""

    specs: tuple[tuple[str, str, str, str, bool, str], ...] = (
        (
            "🤗",
            ui_text(lang, "hero_pill_4").removeprefix("🤗 "),
            HF_DATASET_URL,
            "Hugging Face dataset",
            False,
            "kfps-pill-dataset",
        ),
        ("github", ui_text(lang, "hero_pill_5"), PUBLIC_GITHUB_REPO_URL, "GitHub", False, ""),
        (
            "📄",
            ui_text(lang, "hero_pill_docs"),
            docs_page_url(),
            ui_text(lang, "hero_docs_aria"),
            True,
            "",
        ),
        (
            "⚖",
            ui_text(lang, "hero_pill_license"),
            PUBLIC_GITHUB_LICENSE_URL,
            ui_text(lang, "hero_license_aria"),
            False,
            "kfps-pill-license",
        ),
    )

    cls_link = "kfps-footer-badge kfps-pill-link" if footer else "kfps-pill kfps-pill-link"

    parts: list[str] = []

    for icon, label, href, aria_label, same_tab, extra_class in specs:
        if icon == "github":
            icon_html = GITHUB_PILL_ICON_HTML

        else:
            icon_html = (
                f'<span class="kfps-pill-emoji" aria-hidden="true">{html.escape(icon)}</span>'
            )

        safe_label = html.escape(label)

        safe_href = html.escape(href)

        safe_aria = html.escape(aria_label)

        safe_class = f"{cls_link} {extra_class}".strip()

        target = "" if same_tab else ' target="_blank"'

        rel_attr = "" if same_tab else ' rel="noreferrer"'

        parts.append(
            f'<a class="{safe_class}" href="{safe_href}"{target}{rel_attr} '
            f'aria-label="{safe_aria}">{icon_html}<span>{safe_label}</span></a>'
        )

    return "".join(parts)


def hero_badges_html(lang: str) -> str:

    return nav_link_pills_html(lang, footer=False)


def utility_badges_html(lang: str, *, badge_class: str) -> str:

    assert badge_class == "kfps-footer-badge"

    return nav_link_pills_html(lang, footer=True)


def render_sidebar_title(lang: str) -> None:

    title = html.escape(ui_text(lang, "setup"))

    st.html(
        f"""

        <div class="kfps-sidebar-title">

          <span class="material-symbols-rounded kfps-sidebar-gear"

                aria-hidden="true">settings</span>

          <span>{title}</span>

        </div>

        """
    )


def render_section_band(
    title: str,
    caption: str,
    *,
    light: bool = False,
    variant: str = "",
) -> None:

    mode = " light" if light else ""

    variant_class = f" {variant}" if variant else ""

    safe_title = html.escape(title)

    safe_caption = html.escape(caption)

    st.html(
        f"""

        <section class="kfps-section-band{mode}{variant_class}">

          <div class="kfps-section-band-inner">

            <h2>{safe_title}</h2>

            <p>{safe_caption}</p>

          </div>

        </section>

        """
    )


def render_header(lang: str) -> None:

    hero_main = html.escape(ui_text(lang, "hero_main"))

    hero_subtext = html.escape(ui_text(lang, "hero_subtext"))

    hero_eyebrow = html.escape(ui_text(lang, "hero_eyebrow"))

    badges_html = hero_badges_html(lang)

    st.html(
        f"""

        <section class="kfps-hero">

          <div class="kfps-hero-eyebrow" aria-label="Release context">{hero_eyebrow}</div>

          <div class="kfps-hero-copy" aria-label="Tool summary">

            <span class="kfps-hero-main">{hero_main}</span>

            <span class="kfps-hero-subtext">{hero_subtext}</span>

          </div>

          <div class="kfps-hero-pills" aria-label="Run context">

            {badges_html}

          </div>

        </section>

        """
    )


def render_quick_guide(lang: str) -> None:

    cards = [
        (
            "guide_1_title",
            "guide_1_body",
            "guide_1_detail",
            "edit_note",
        ),
        (
            "guide_2_title",
            "guide_2_body",
            "guide_2_detail",
            "groups",
        ),
        (
            "guide_3_title",
            "guide_3_body",
            "guide_3_detail",
            "paid",
        ),
        (
            "guide_4_title",
            "guide_4_body",
            "guide_4_detail",
            "description",
        ),
    ]

    card_html = []

    for title_key, body_key, detail_key, icon_name in cards:
        card_html.append(
            f"""

            <details class="kfps-flow-card" name="kfps-flow">

              <summary>

                <div class="kfps-icon" aria-hidden="true">

                  <span class="material-symbols-rounded kfps-step-icon">

                    {html.escape(icon_name)}

                  </span>

                </div>

                <h3>{html.escape(ui_text(lang, title_key))}</h3>

                <p>{html.escape(ui_text(lang, body_key))}</p>

              </summary>

              <div class="kfps-flow-detail">{html.escape(ui_text(lang, detail_key))}</div>

            </details>

            """
        )

    st.html(
        f"""

        <section class="kfps-guide">

          <div class="kfps-guide-inner">

            <div class="kfps-eyebrow">{html.escape(ui_text(lang, "guide_eyebrow"))}</div>

            <h2>{html.escape(ui_text(lang, "guide_title"))}</h2>

            <div class="kfps-flow">

              {"".join(card_html)}

            </div>

          </div>

        </section>

        """
    )


def render_secrets_status(lang: str) -> None:

    status = secrets_loader.load_secrets_from_env_path()
    with st.expander(ui_text(lang, "secrets_status_header"), expanded=False):
        if not status.env_path_exists:
            st.warning(ui_text(lang, "env_file_missing"))

        providers = (
            ("OpenAI", status.openai_present, ui_text(lang, "openai_key_help")),
            ("Anthropic", status.anthropic_present, ui_text(lang, "anthropic_key_help")),
            ("Google", status.google_present, ui_text(lang, "google_key_help")),
            ("Groq", status.groq_present, ui_text(lang, "provider_key_help")),
            ("DeepSeek", status.deepseek_present, ui_text(lang, "provider_key_help")),
            ("Qwen", status.qwen_present, ui_text(lang, "provider_key_help")),
            ("HF Token", status.hf_token_present, ui_text(lang, "hf_status_help")),
            ("KOSIS", status.kosis_api_key_present, ui_text(lang, "kosis_status_help")),
        )

        cards = []

        for label, present, help_text in providers:
            state_class = "ok" if present else "missing"

            mark = ui_text(lang, "secret_present") if present else ui_text(lang, "secret_missing")

            cards.append(
                f"""

                <div class="kfps-secret-status-card">

                  <span class="kfps-secret-provider">{html.escape(label)}</span>

                  <span class="kfps-secret-state {state_class}">{html.escape(mark)}</span>

                  <span class="kfps-help-dot" data-tooltip="{html.escape(help_text, quote=True)}"

                        aria-label="{html.escape(help_text, quote=True)}" tabindex="0">?</span>

                </div>

                """
            )

        st.html(f'<div class="kfps-secret-status-grid">{"".join(cards)}</div>')


def render_concept_inputs(lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "concept_header"))

    render_input_section_heading(ui_text(lang, "input_section_basics"))

    basic_project_col, basic_category_col, basic_price_col = st.columns(3, gap="small")

    with basic_project_col:
        project_name = st.text_input(ui_text(lang, "project_name"), max_chars=100)

    with basic_category_col:
        category = st.text_input(
            ui_text(lang, "category"),
            placeholder=ui_text(lang, "category_placeholder"),
            max_chars=80,
        )

    with basic_price_col:
        product_price_krw = st.number_input(
            ui_text(lang, "price"),
            min_value=1,
            max_value=10_000_000_000,
            value=159_000,
            step=10_000,
        )

    render_input_section_heading(ui_text(lang, "input_section_style"))

    season_col, occasion_col, style_col = st.columns(3, gap="small")

    with season_col:
        season = st.text_input(
            ui_text(lang, "season"),
            placeholder=ui_text(lang, "season_placeholder"),
            max_chars=40,
        )

    with occasion_col:
        occasion = st.text_input(
            ui_text(lang, "occasion"),
            placeholder=ui_text(lang, "occasion_placeholder"),
            max_chars=120,
        )

    with style_col:
        style_tone = st.text_input(
            ui_text(lang, "style_tone"),
            placeholder=ui_text(lang, "style_tone_placeholder"),
            max_chars=80,
        )

    render_input_section_heading(ui_text(lang, "input_section_product"))

    fit_col, material_col, color_col = st.columns(3, gap="small")

    with fit_col:
        fit = st.text_input(
            ui_text(lang, "fit"),
            placeholder=ui_text(lang, "fit_placeholder"),
            max_chars=80,
        )

    with material_col:
        material = st.text_input(
            ui_text(lang, "material"),
            placeholder=ui_text(lang, "material_placeholder"),
            max_chars=80,
        )

    with color_col:
        color = st.text_input(
            ui_text(lang, "color"),
            placeholder=ui_text(lang, "color_placeholder"),
            max_chars=80,
        )

    render_input_section_heading(ui_text(lang, "input_section_target"))

    description_col, target_col, run_col = st.columns([1.35, 0.9, 0.9], gap="small")

    with description_col:
        description = st.text_area(
            ui_text(lang, "concept_text"),
            placeholder=ui_text(lang, "concept_placeholder"),
            max_chars=3000,
            height=272,
            key="kfps_concept_description",
        )

    with target_col:
        target_hypothesis = st.text_area(
            ui_text(lang, "target"),
            placeholder=ui_text(lang, "target_placeholder"),
            max_chars=1000,
            height=272,
            key="kfps_target_hypothesis",
        )

    with run_col, st.container(key="kfps_enter_overlay"):
        render_enter_card(lang)

        enter_button_placeholder = st.empty()

    raw_fields: dict[str, Any] = {
        "category": category,
        "price": int(product_price_krw),
        "fit": fit,
        "material": material,
        "color": color,
        "season": season,
        "occasion": occasion,
        "style_tone": style_tone,
        "target_hypothesis": target_hypothesis,
        "description": description,
    }

    canonical_text = build_canonical_product_card_text(raw_fields)

    return {
        "project_name": project_name.strip() or "k-fashion-persona",
        "category": category.strip(),
        "product_price_krw": int(product_price_krw),
        "fit": fit.strip(),
        "material": material.strip(),
        "color": color.strip(),
        "season": season.strip(),
        "occasion": occasion.strip(),
        "style_tone": style_tone.strip(),
        "target_hypothesis": target_hypothesis.strip(),
        "description": normalize_concept_text(description),
        "canonical_product_card_text": canonical_text,
        "concept_text": canonical_text,
        "_enter_button_placeholder": enter_button_placeholder,
    }


def render_enter_button(placeholder: Any, lang: str, *, disabled: bool) -> None:
    """Paint ENTER into the slot created beside concept inputs (disabled follows run guards)."""

    with placeholder.container():
        if st.button(
            ui_text(lang, "run_button"),
            key="kfps_enter_card_button",
            use_container_width=True,
            disabled=disabled,
        ):
            st.session_state["kfps_enter_requested"] = True


def render_dataset_inputs(lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "dataset_header"))

    source = st.radio(
        ui_text(lang, "source"),
        ["huggingface", "local"],
        format_func=lambda v: ui_text(lang, "hf") if v == "huggingface" else ui_text(lang, "local"),
        horizontal=True,
    )

    if source == "huggingface":
        st.text_input(
            "HF dataset_id",
            value=DEFAULT_HF_DATASET_ID,
            disabled=True,
            help="공개판의 Hugging Face 연결은 이 데이터셋으로 고정해.",
        )

        split = st.text_input("split", value=DEFAULT_SPLIT)

        revision = st.text_input(
            "revision",
            help="선택 사항. 같은 데이터 버전 재현이 필요하면 dataset commit SHA를 넣어.",
        )

        return {
            "source": source,
            "dataset_id": DEFAULT_HF_DATASET_ID,
            "split": split.strip() or DEFAULT_SPLIT,
            "revision": revision.strip() or None,
        }

    local_path = st.text_input(ui_text(lang, "local_path"))

    return {"source": source, "local_path": local_path.strip()}


def render_sample_inputs(lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "panel_header"))

    sample_size = st.number_input(
        ui_text(lang, "sample_size"),
        min_value=1,
        max_value=MAX_SAMPLE_SIZE,
        value=30,
        step=10,
        help=ui_text(lang, "sample_help").format(max_sample=MAX_SAMPLE_SIZE),
    )

    sampling_seed = st.number_input(
        ui_text(lang, "sampling_seed"),
        min_value=0,
        value=42,
        step=1,
        help=ui_text(lang, "sampling_seed_help"),
    )

    age_min, age_max = st.slider(ui_text(lang, "age"), min_value=0, max_value=100, value=(0, 100))

    sex = st.multiselect(ui_text(lang, "sex"), ["M", "F"])

    province = st.multiselect(
        ui_text(lang, "province"),
        KOREA_PROVINCE_OPTIONS,
        help=ui_text(lang, "province_help"),
    )

    occupation = st.multiselect(
        ui_text(lang, "occupation"),
        OCCUPATION_KEYWORD_OPTIONS,
        help=ui_text(lang, "occupation_help"),
    )

    return {
        "sample_size": int(sample_size),
        "sampling_seed": int(sampling_seed),
        "filter": PersonaFilter(
            age_min=int(age_min) if age_min > 0 else None,
            age_max=int(age_max) if age_max < 100 else None,
            sex=frozenset(sex),
            province=frozenset(province),
            occupation_contains=frozenset(occupation),
        ),
    }


def render_model_inputs(pricing_config: dict[str, ModelPricing], lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "model_header"))

    model_options = _sorted_model_options(pricing_config)

    if not model_options:
        st.error(ui_text(lang, "model_missing"))

        return {}

    model_alias = st.selectbox(
        ui_text(lang, "model"),
        model_options,
        format_func=lambda alias: _model_option_label(alias, pricing_config),
    )

    pricing = get_model_pricing(pricing_config, model_alias)

    model_name = pricing.provider_model_id or model_alias

    render_model_metadata(pricing, model_name, lang=lang)

    if notice := _provider_key_policy_notice(lang):
        st.info(notice)

    temperature = st.slider("temperature", 0.0, 1.0, DEFAULT_TEMPERATURE, 0.1)

    api_override = str(st.session_state.get("kfps_api_key", ""))

    hf_override = str(st.session_state.get("kfps_hf_token", ""))

    secrets_status = secrets_loader.load_secrets_from_env_path()
    api_label = ui_text(lang, "api_key").format(provider=pricing.provider)

    api_key = render_secret_password_input(
        api_label,
        placeholder=ui_text(lang, "api_key_placeholder"),
        key="kfps_api_key",
        present=bool(_safe_provider_key(pricing.provider, api_override, pricing.api_key_env)),
        help_text=ui_text(lang, "api_key_help"),
    )

    hf_token = render_secret_password_input(
        ui_text(lang, "hf_token"),
        placeholder=ui_text(lang, "hf_token_placeholder"),
        key="kfps_hf_token",
        present=bool(hf_override.strip()) or secrets_status.hf_token_present,
        help_text=ui_text(lang, "hf_token_help"),
    )

    return {
        "model_alias": model_alias,
        "model_name": model_name,
        "provider": pricing.provider,
        "pricing": pricing,
        "temperature": float(temperature),
        "api_key": api_key,
        "hf_token": hf_token,
    }


def _safe_kosis_api_key(override: str) -> str | None:

    override = override.strip()

    if override:
        return override

    return secrets_loader.get_kosis_api_key()


def render_kosis_inputs(lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "kosis_header"))

    options = kosis_segment_options()

    option_labels = {label: key for key, label in options.items()}

    default_label = options.get(DEFAULT_REFERENCE_SEGMENT_ID, DEFAULT_REFERENCE_SEGMENT_LABEL)

    selected_label = st.selectbox(
        ui_text(lang, "kosis_segment"),
        list(option_labels.keys()),
        index=list(option_labels.keys()).index(default_label),
        help=ui_text(lang, "kosis_segment_help"),
        key="kfps_kosis_segment",
    )

    kosis_override = str(st.session_state.get("kfps_kosis_api_key", ""))

    secrets_status = secrets_loader.load_secrets_from_env_path()
    kosis_api_key = render_secret_password_input(
        ui_text(lang, "kosis_api_key"),
        placeholder=ui_text(lang, "kosis_api_key_placeholder"),
        key="kfps_kosis_api_key",
        present=bool(_safe_kosis_api_key(kosis_override)) or secrets_status.kosis_api_key_present,
        help_text=ui_text(lang, "kosis_api_key_help"),
    )

    use_api_refresh = st.checkbox(
        ui_text(lang, "kosis_refresh"),
        value=False,
        key="kfps_kosis_refresh",
    )

    default_url = os.environ.get(KOSIS_STATISTICS_URL_VAR, "")

    api_url = st.text_input(
        ui_text(lang, "kosis_api_url"),
        value=default_url,
        placeholder=ui_text(lang, "kosis_api_url_placeholder"),
        help=ui_text(lang, "kosis_api_url_help"),
        key="kfps_kosis_api_url",
        disabled=not use_api_refresh,
    )

    return {
        "reference_segment_id": option_labels[str(selected_label or default_label)],
        "api_key": kosis_api_key,
        "api_url": api_url,
        "use_api_refresh": bool(use_api_refresh),
    }


def render_simple_setup(pricing_config: dict[str, ModelPricing], lang: str) -> dict[str, Any]:

    st.subheader(ui_text(lang, "quick_setup_header"))

    st.caption(ui_text(lang, "quick_setup_caption"))

    mode_labels = {
        _run_mode_label(lang, "quick"): "quick",
        _run_mode_label(lang, "balanced"): "balanced",
        _run_mode_label(lang, "deep"): "deep",
        _run_mode_label(lang, "max"): "max",
    }

    if st.session_state.get("kfps_run_mode") not in mode_labels:
        st.session_state.pop("kfps_run_mode", None)

    selected_mode_label = st.segmented_control(
        ui_text(lang, "run_mode"),
        options=list(mode_labels.keys()),
        default=_run_mode_label(lang, "balanced"),
        key="kfps_run_mode",
    )

    run_mode = mode_labels[str(selected_mode_label or _run_mode_label(lang, "balanced"))]

    preset = RUN_MODE_PRESETS[run_mode]

    render_inline_note(ui_text(lang, f"mode_{run_mode}_help"), extra_class="kfps-run-mode-note")

    model_options = _sorted_model_options(pricing_config)

    if not model_options:
        st.error(ui_text(lang, "model_missing"))

        return {}

    default_alias = _default_model_alias(model_options)

    pricing = get_model_pricing(pricing_config, default_alias)

    model_alias = default_alias

    model_name = pricing.provider_model_id or model_alias

    sample_size = int(preset["sample_size"])

    sampling_seed = 42

    temperature = float(preset["temperature"])

    dataset: dict[str, Any] = {
        "source": "huggingface",
        "dataset_id": DEFAULT_HF_DATASET_ID,
        "split": DEFAULT_SPLIT,
        "revision": None,
    }

    sample = {
        "sample_size": sample_size,
        "sampling_seed": sampling_seed,
        "filter": PersonaFilter(),
    }

    with st.expander(
        ui_text(lang, "advanced_header"),
        expanded=False,
        key="kfps_advanced_expander",
        on_change="ignore",
    ):
        st.caption(ui_text(lang, "advanced_caption"))

        dataset = render_dataset_inputs(lang)

        st.subheader(ui_text(lang, "panel_header"))

        sample_size = st.number_input(
            ui_text(lang, "sample_size"),
            min_value=1,
            max_value=MAX_SAMPLE_SIZE,
            value=sample_size,
            step=10,
            help=ui_text(lang, "sample_help").format(max_sample=MAX_SAMPLE_SIZE),
        )

        sampling_seed = st.number_input(
            ui_text(lang, "sampling_seed"),
            min_value=0,
            value=sampling_seed,
            step=1,
            help=ui_text(lang, "sampling_seed_help"),
        )

        age_min, age_max = st.slider(
            ui_text(lang, "age"),
            min_value=0,
            max_value=100,
            value=(0, 100),
        )

        sex = st.multiselect(ui_text(lang, "sex"), ["M", "F"])

        province = st.multiselect(
            ui_text(lang, "province"),
            KOREA_PROVINCE_OPTIONS,
            help=ui_text(lang, "province_help"),
        )

        occupation = st.multiselect(
            ui_text(lang, "occupation"),
            OCCUPATION_KEYWORD_OPTIONS,
            help=ui_text(lang, "occupation_help"),
        )

        sample = {
            "sample_size": int(sample_size),
            "sampling_seed": int(sampling_seed),
            "filter": PersonaFilter(
                age_min=int(age_min) if age_min > 0 else None,
                age_max=int(age_max) if age_max < 100 else None,
                sex=frozenset(sex),
                province=frozenset(province),
                occupation_contains=frozenset(occupation),
            ),
        }

        temperature = st.slider("temperature", 0.0, 1.0, temperature, 0.1)

    st.caption(
        ui_text(lang, "simple_summary").format(
            mode=_run_mode_label(lang, run_mode),
            sample_size=sample["sample_size"],
            temperature=temperature,
        )
    )

    st.markdown(f"**{ui_text(lang, 'model_header')}**")

    model_alias = st.selectbox(
        ui_text(lang, "model"),
        model_options,
        index=model_options.index(model_alias),
        key="kfps_model_alias",
        format_func=lambda alias: _model_option_label(alias, pricing_config),
    )

    pricing = get_model_pricing(pricing_config, model_alias)

    model_name = pricing.provider_model_id or model_alias

    render_model_metadata(pricing, model_name, sample_size=int(sample["sample_size"]), lang=lang)

    api_override = str(st.session_state.get("kfps_api_key", ""))

    hf_override = str(st.session_state.get("kfps_hf_token", ""))

    secrets_status = secrets_loader.load_secrets_from_env_path()
    api_label = ui_text(lang, "api_key").format(provider=pricing.provider)

    api_key = render_secret_password_input(
        api_label,
        placeholder=ui_text(lang, "api_key_placeholder"),
        key="kfps_api_key",
        present=bool(_safe_provider_key(pricing.provider, api_override, pricing.api_key_env)),
        help_text=ui_text(lang, "api_key_help"),
    )

    hf_token = render_secret_password_input(
        ui_text(lang, "hf_token"),
        placeholder=ui_text(lang, "hf_token_placeholder"),
        key="kfps_hf_token",
        present=bool(hf_override.strip()) or secrets_status.hf_token_present,
        help_text=ui_text(lang, "hf_token_help"),
    )

    kosis = render_kosis_inputs(lang)

    return {
        "dataset": dataset,
        "sample": sample,
        "model": {
            "model_alias": model_alias,
            "model_name": model_name,
            "provider": pricing.provider,
            "pricing": pricing,
            "temperature": float(temperature),
            "api_key": api_key,
            "hf_token": hf_token,
        },
        "kosis": kosis,
    }


def make_price_context(
    product_price_krw: int,
    kosis: dict[str, Any] | None = None,
) -> dict[str, Any]:

    kosis = kosis or {}

    return build_price_context(
        product_price_krw,
        reference_segment_id=str(kosis.get("reference_segment_id") or DEFAULT_REFERENCE_SEGMENT_ID),
        use_api_refresh=bool(kosis.get("use_api_refresh")),
        kosis_api_key=str(_safe_kosis_api_key(str(kosis.get("api_key", ""))) or ""),
        kosis_api_url=str(kosis.get("api_url", "")),
    )


def render_price_context(price_context: dict[str, Any], lang: str) -> None:

    st.subheader(ui_text(lang, "price_context_header"))

    denom = f"{int(price_context.get('denominator_krw', KOSTAT_2025_ANNUAL_CLOTHING_KRW)):,}"

    st.write(
        "제품 가격이 연간 환산 의류·신발 지출 기준의 "
        f"**{price_context['price_burden_ratio']:.2f}배** 수준이야. "
        f"기준값: {denom} KRW, 라벨: **{price_context['price_burden_label']}**"
    )

    st.caption(
        "KOSIS 기준 계층: "
        f"{price_context.get('reference_segment_label', DEFAULT_REFERENCE_SEGMENT_LABEL)}"
        f" · 기간: {price_context.get('period', '')}"
        f" · 소스: {price_context.get('source_mode', 'snapshot')}"
    )

    for warning in price_context.get("warnings", ()):
        st.warning(str(warning))

    st.caption(ui_text(lang, "price_context_caption"))


def make_cost_state(
    concept: dict[str, Any],
    sample: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any]:

    if not concept.get("description"):
        return {"ready": False}

    cached_count = 0

    new_call_count = sample["sample_size"] - cached_count

    concept_tokens = count_tokens_approx(concept["concept_text"])

    token_est = _estimate_run_tokens(new_call_count, concept_tokens)

    cost_est = _estimate_model_cost(token_est, model["pricing"])

    return {
        "ready": True,
        "new_call_count": new_call_count,
        "token_estimate": token_est,
        "cost_estimate": cost_est,
        "pricing": model["pricing"],
    }


def render_cost_estimate(cost_state: dict[str, Any], lang: str) -> None:

    st.subheader(ui_text(lang, "cost_header"))

    if not cost_state.get("ready"):
        render_inline_note(ui_text(lang, "need_concept"))

        return

    cost_est = cost_state["cost_estimate"]

    token_est = cost_state["token_estimate"]

    pricing = cost_state["pricing"]

    c1, c2, c3 = st.columns(3)

    c1.metric(ui_text(lang, "new_calls"), f"{cost_state['new_call_count']}명")

    c2.metric(
        ui_text(lang, "estimated_cost"),
        _format_cost_range(cost_est) if cost_est else ui_text(lang, "price_unset"),
    )

    if cost_est is not None:
        c3.metric(
            ui_text(lang, "estimated_time"),
            f"{cost_est.estimated_time_min_low:.1f} - {cost_est.estimated_time_min_high:.1f}분",
        )
    else:
        c3.metric(ui_text(lang, "estimated_time"), ui_text(lang, "estimate_only"))

    output_cap_value = (
        f"{ESTIMATE_OUTPUT_TOKENS_PER_PERSONA} / {MAX_OUTPUT_TOKENS_PER_PERSONA} tokens per persona"
    )

    breakdown_rows = [
        (ui_text(lang, "rate_unit_label"), ui_text(lang, "per_million_tokens")),
        (
            ui_text(lang, "run_tokens_label"),
            (
                f"{_format_tokens(token_est.estimated_input_tokens_total)} input / "
                f"{_format_tokens(token_est.estimated_output_tokens_total)} output"
            ),
        ),
        (
            ui_text(lang, "cost_input_label"),
            _format_usd(_input_cost_usd(token_est, pricing))
            if pricing.input_per_million_usd is not None
            else ui_text(lang, "price_unset"),
        ),
        (
            ui_text(lang, "cost_output_label"),
            _format_usd(_output_cost_usd(token_est, pricing))
            if pricing.output_per_million_usd is not None
            else ui_text(lang, "price_unset"),
        ),
        (
            ui_text(lang, "cost_max_output_label"),
            output_cap_value,
        ),
    ]

    row_html = "".join(
        '<div class="kfps-model-meta-row">'
        f'<span class="kfps-model-meta-label">{html.escape(label)}</span>'
        f'<span class="kfps-model-meta-value">{html.escape(value)}</span>'
        "</div>"
        for label, value in breakdown_rows
    )

    st.html(f'<div class="kfps-model-meta">{row_html}</div>')

    st.caption(ui_text(lang, "cost_caption"))

    st.caption(ui_text(lang, "cost_unit_note"))


def render_model_cost_comparison(
    pricing_config: dict[str, ModelPricing],
    token_est: TokenEstimate,
    lang: str,
) -> None:

    st.subheader(ui_text(lang, "model_compare_header"))

    st.caption(ui_text(lang, "model_compare_caption"))

    rows: list[tuple[float, str, str, str, str]] = []

    for alias, pricing in pricing_config.items():
        cost_est = _estimate_model_cost(token_est, pricing)
        provider = _provider_display_name(pricing.provider, pricing.api_key_env)
        rate = (
            f"{_format_price(pricing.input_per_million_usd, lang)} / "
            f"{_format_price(pricing.output_per_million_usd, lang)}"
        )
        if cost_est is None:
            rows.append((float("inf"), alias, provider, rate, ui_text(lang, "price_unset")))
            continue

        rows.append(
            (
                cost_est.estimated_cost_usd_low,
                alias,
                provider,
                rate,
                _format_cost_range(cost_est),
            )
        )

    rows.sort(key=lambda row: (row[0], row[1]))

    header_cells = (
        ui_text(lang, "cost_table_model"),
        ui_text(lang, "cost_table_provider"),
        ui_text(lang, "cost_table_rate"),
        ui_text(lang, "cost_table_estimate"),
    )

    header_html = "".join(f"<th>{html.escape(cell)}</th>" for cell in header_cells)

    body_html = "".join(
        "<tr>"
        f"<td>{html.escape(alias)}</td>"
        f"<td>{html.escape(provider)}</td>"
        f"<td>{html.escape(rate)}</td>"
        f"<td>{html.escape(estimate)}</td>"
        "</tr>"
        for _low, alias, provider, rate, estimate in rows
    )

    st.html(
        '<div class="kfps-cost-table-wrap"><table class="kfps-cost-table">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{body_html}</tbody>"
        "</table></div>"
    )


def _normalize_card_field(value: Any) -> str:

    text = normalize_concept_text("" if value is None else str(value))

    return text or PRODUCT_CARD_EMPTY_PLACEHOLDER


def _format_card_price(value: Any) -> str:

    try:
        price_int = int(value)

    except (TypeError, ValueError):
        return PRODUCT_CARD_EMPTY_PLACEHOLDER

    if price_int <= 0:
        return PRODUCT_CARD_EMPTY_PLACEHOLDER

    return f"{price_int:,}원"


def build_canonical_product_card_text(fields: dict[str, Any]) -> str:
    """Render the canonical product card text (locked field order and labels).



    The format is fixed: 10 lines, one per field, in PRODUCT_CARD_FIELD_ORDER.

    Each value is normalised through normalize_concept_text (NFC + invisible

    char strip + whitespace collapse + trim) so that semantically identical

    user input always produces an identical canonical string. Empty values

    collapse to "미입력". The price field is formatted as `{:,}원`.



    The downstream concept_hash uses this canonical text, so the hash is

    stable across re-renders of the same product card and a single field

    change always changes the hash.

    """

    lines: list[str] = []

    for key in PRODUCT_CARD_FIELD_ORDER:
        label = PRODUCT_CARD_FIELD_LABELS_KR[key]

        if key == "price":
            normalized = _format_card_price(fields.get(key, fields.get("product_price_krw", 0)))

        else:
            normalized = _normalize_card_field(fields.get(key, ""))

        lines.append(f"{label}: {normalized}")

    return "\n".join(lines)


def make_hashes(
    concept: dict[str, Any],
    price_context: dict[str, Any] | None = None,
) -> dict[str, str]:

    concept_hash = compute_concept_hash(
        concept["concept_text"],
        concept["category"],
        concept["product_price_krw"],
    )

    price_context = price_context or make_price_context(concept["product_price_krw"])

    price_context_hash = compute_price_context_hash(
        source=str(price_context.get("source", "kosis")),
        period=str(price_context.get("period", "")),
        denominator_krw=int(price_context.get("denominator_krw", KOSTAT_2025_ANNUAL_CLOTHING_KRW)),
        price_context_version=DEFAULT_PRICE_CONTEXT_VERSION,
        context_digest=str(price_context.get("context_digest", "")),
    )

    return {"concept_hash": concept_hash, "price_context_hash": price_context_hash}


def render_hashes(hashes: dict[str, str], lang: str) -> None:

    with st.expander(ui_text(lang, "debug_hash")):
        st.code(
            f"concept_hash: {hashes['concept_hash']}\n"
            f"price_context_hash: {hashes['price_context_hash']}"
        )


def render_run_panel(lang: str) -> None:

    st.html(
        f"""

        <section class="kfps-run-panel">

          <h3>{html.escape(ui_text(lang, "run_confirm_header"))}</h3>

          <p>{html.escape(ui_text(lang, "run_panel_body"))}</p>

        </section>

        """
    )


def render_report_placeholder(lang: str) -> None:

    _, export_col = st.columns([4, 1])

    with export_col:
        st.download_button(
            ui_text(lang, "report_export_button"),
            data="",
            file_name="k-fashion-persona-report.md",
            mime="text/markdown",
            key="kfps_export_md_pending",
            type="primary",
            use_container_width=True,
            disabled=True,
        )

    st.html(
        f"""

        <span class="kfps-result-anchor" data-kfps-anchor="report-markdown"></span>

        <section class="kfps-report-shell kfps-report-empty" aria-live="polite">

          <div>

            <strong>{html.escape(ui_text(lang, "report_placeholder_title"))}</strong>

            <span>{html.escape(ui_text(lang, "report_placeholder_body"))}</span>

            <span>{html.escape(ui_text(lang, "report_placeholder_hint"))}</span>

          </div>

        </section>

        """
    )


def render_detailed_run_context(
    price_context: dict[str, Any],
    cost_state: dict[str, Any],
    hashes: dict[str, str],
    lang: str,
    pricing_config: dict[str, ModelPricing] | None = None,
) -> None:

    with st.expander(ui_text(lang, "details_header"), expanded=False):
        st.caption(ui_text(lang, "details_summary"))

        render_price_context(price_context, lang)

        render_cost_estimate(cost_state, lang)

        if pricing_config and cost_state.get("ready"):
            render_model_cost_comparison(pricing_config, cost_state["token_estimate"], lang)

        render_hashes(hashes, lang)


def scroll_to_persona_results_once() -> None:

    if not st.session_state.pop("scroll_to_persona_results", False):
        return

    components.html(
        """

        <script>

        requestAnimationFrame(() => {

          const target = window.parent.document.querySelector(

            '[data-kfps-anchor="persona-results"]'

          );

          if (target) {

            target.scrollIntoView({ behavior: "smooth", block: "start" });

          }

        });

        </script>

        """,
        height=0,
    )


def scroll_to_report_panel_once() -> None:

    components.html(
        """

        <script>

        requestAnimationFrame(() => {

          const target = window.parent.document.querySelector(

            '[data-kfps-anchor="report-markdown"]'

          );

          if (target) {

            target.scrollIntoView({ behavior: "smooth", block: "start" });

          }

        });

        </script>

        """,
        height=0,
    )


def render_persona_results_anchor() -> None:

    st.html('<span class="kfps-result-anchor" data-kfps-anchor="persona-results"></span>')


def render_loading_panel(lang: str) -> None:

    st.html(
        f"""

        <section class="kfps-loading-panel" role="status" aria-live="polite">

          <span class="kfps-dot-spinner" aria-hidden="true"></span>

          <div>

            <strong>{html.escape(ui_text(lang, "results_loading"))}</strong>

          </div>

        </section>

        """
    )


def _persona_profile(persona_id: str, attrs: dict[str, Any]) -> str:

    values = [
        f"{attrs.get('age')}세" if attrs.get("age") is not None else "",
        str(attrs.get("sex", "")),
        str(attrs.get("province", "")),
        str(attrs.get("occupation", "")),
    ]

    profile = " / ".join(value for value in values if value)

    return profile or persona_id


def build_persona_opinion_rows(
    result_rows: list[ResultRow],
    persona_attributes: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:

    rows: list[dict[str, str]] = []

    for row in result_rows:
        if row["status"] not in {"success", "cached"} or not row["response_json"]:
            continue

        parsed: EvaluationResult | None = None

        try:
            parsed = validate_evaluation_payload(json.loads(row["response_json"]))

        except json.JSONDecodeError:
            logger.warning(
                "Skipping persona opinion row with invalid cached JSON.",
                extra={"reason": "json_decode", "persona_id": row.get("persona_id")},
            )

        except ValidationError:
            logger.warning(
                "Skipping persona opinion row with invalid result schema.",
                extra={"reason": "schema_validation", "persona_id": row.get("persona_id")},
            )

        except TypeError:
            logger.warning(
                "Skipping persona opinion row with non-string response JSON.",
                extra={"reason": "response_json_type", "persona_id": row.get("persona_id")},
            )

            parsed = None

        if parsed is None:
            continue

        attrs = persona_attributes.get(parsed.persona_id, {})

        rows.append(
            {
                "persona_id": parsed.persona_id,
                "profile": _persona_profile(parsed.persona_id, attrs),
                "sentiment": parsed.sentiment,
                "interest_score": str(parsed.interest_score),
                "price_burden": parsed.price_burden,
                "main_reasons": " / ".join(parsed.main_reasons),
                "main_concerns": " / ".join(parsed.main_concerns),
                "confidence_note": parsed.confidence_note,
            }
        )

    return rows


def persona_opinions_csv(rows: list[dict[str, str]]) -> str:

    fieldnames = [
        "persona_id",
        "profile",
        "sentiment",
        "interest_score",
        "price_burden",
        "main_reasons",
        "main_concerns",
        "confidence_note",
    ]

    output = io.StringIO(newline="")

    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    writer.writerows(rows)

    return "\ufeff" + output.getvalue()


def render_persona_opinion_preview(
    result_rows: list[ResultRow],
    persona_attributes: dict[str, dict[str, Any]],
    project_name: str,
    job_id: str,
    lang: str,
) -> None:

    opinion_rows = build_persona_opinion_rows(result_rows, persona_attributes)

    if not opinion_rows:
        render_inline_note(ui_text(lang, "persona_preview_empty"))

        return

    st.html(
        f"""

        <div class="kfps-opinion-head">

          <div>

            <h3>{html.escape(ui_text(lang, "results_preview_header"))}</h3>

            <p>{html.escape(ui_text(lang, "results_preview_body"))}</p>

          </div>

        </div>

        """
    )

    cards = []

    for row in opinion_rows[:5]:
        sentiment = html.escape(row["sentiment"])

        cards.append(
            f"""

            <article class="kfps-opinion-card">

              <div class="kfps-opinion-meta">

                <span>{html.escape(row["persona_id"])}</span>

                <span class="kfps-sentiment {sentiment}">{sentiment}</span>

              </div>

              <p class="kfps-opinion-profile">{html.escape(row["profile"])}</p>

              <h4>{html.escape(ui_text(lang, "persona_card_reasons"))}</h4>

              <p>{html.escape(row["main_reasons"] or "-")}</p>

              <h4>{html.escape(ui_text(lang, "persona_card_concerns"))}</h4>

              <p>{html.escape(row["main_concerns"] or "-")}</p>

              <h4>{html.escape(ui_text(lang, "persona_card_note"))}</h4>

              <p>{html.escape(row["confidence_note"])}</p>

            </article>

            """
        )

    st.html(f'<div class="kfps-opinion-grid">{"".join(cards)}</div>')

    st.download_button(
        ui_text(lang, "excel_download"),
        data=persona_opinions_csv(opinion_rows),
        file_name=f"{project_name}-{job_id}-persona-opinions.csv",
        mime="text/csv",
    )
