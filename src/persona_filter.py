# SPDX-License-Identifier: AGPL-3.0-only
"""Persona 필터링 + 샘플링.

PM v3 §23 Phase 2: 연령/성별/지역/직업 필터, sampling_seed.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from src.persona_normalizer import Persona


@dataclass(frozen=True)
class PersonaFilter:
    """모든 필터는 None / 빈 collection 이면 해당 조건 무시."""

    age_min: int | None = None
    age_max: int | None = None
    sex: frozenset[str] = frozenset()
    province: frozenset[str] = frozenset()
    occupation_contains: frozenset[str] = frozenset()  # 부분 일치 OR

    def matches(self, p: Persona) -> bool:
        if self.age_min is not None and p.age < self.age_min:
            return False
        if self.age_max is not None and p.age > self.age_max:
            return False
        if self.sex and p.sex not in self.sex:
            return False
        if self.province and p.province not in self.province:
            return False
        # occupation_contains: case-insensitive 부분 일치 (PM v3 task instructions §2)
        return not (
            self.occupation_contains
            and not any(kw.lower() in p.occupation.lower() for kw in self.occupation_contains)
        )


def apply_filter(
    personas: Iterable[Persona],
    filt: PersonaFilter,
) -> list[Persona]:
    """필터 통과한 persona 만 list 로 수집.

    streaming iterator 를 받을 수 있으나 sample 위해 list 화 필요.
    호출자가 메모리 부담을 인지하고 사용.
    """
    return [p for p in personas if filt.matches(p)]


def has_active_filter(filt: PersonaFilter) -> bool:
    """Return True when any filter condition is active."""
    return any(
        (
            filt.age_min is not None,
            filt.age_max is not None,
            bool(filt.sex),
            bool(filt.province),
            bool(filt.occupation_contains),
        )
    )


def sample_personas(
    personas: list[Persona],
    sample_size: int,
    seed: int,
) -> list[Persona]:
    """sampling_seed 고정 random sample.

    sample_size > 모집단 → 전체 반환 (raise 없음, UI 에서 안내).
    sample_size <= 0 → ValueError.
    """
    if sample_size <= 0:
        raise ValueError(f"sample_size must be positive, got {sample_size}")

    if sample_size >= len(personas):
        # 전체 반환 (sort by persona_id for determinism)
        return sorted(personas, key=lambda p: p.persona_id)

    # Persona 샘플링은 통계적 재현성 (seed 고정) 목적이며 보안/암호 용도가 아니므로
    # secrets 가 아닌 random 사용이 적절하다.
    rng = random.Random(seed)  # nosec B311
    selected = rng.sample(personas, sample_size)
    return sorted(selected, key=lambda p: p.persona_id)


def filter_summary(filt: PersonaFilter) -> str:
    """UI 표시용 요약 문자열."""
    parts = []
    if filt.age_min is not None or filt.age_max is not None:
        lo = filt.age_min if filt.age_min is not None else "*"
        hi = filt.age_max if filt.age_max is not None else "*"
        parts.append(f"연령 {lo}-{hi}세")
    if filt.sex:
        parts.append(f"성별 {','.join(sorted(filt.sex))}")
    if filt.province:
        parts.append(f"지역 {','.join(sorted(filt.province))}")
    if filt.occupation_contains:
        parts.append(f"직업 키워드 {','.join(sorted(filt.occupation_contains))}")
    return " / ".join(parts) if parts else "필터 없음 (전체)"


@dataclass(frozen=True)
class SampleResult:
    """필터 + 샘플링 결과.

    PM v3 §23 Phase 2 / task instructions §2.
    matched_count_before_sample: 필터 통과 총 수 (샘플 전).
    rows: 샘플링된 Persona 리스트.
    """

    rows: list[Persona]
    matched_count_before_sample: int
    sample_size: int
    sampling_seed: int


def sample_to_result(
    personas: list[Persona],
    sample_size: int,
    seed: int,
) -> SampleResult:
    """필터 통과된 personas 에서 sample_size 만큼 샘플링.

    sample_size > matched → matched 만큼 반환.
    matched == 0 → 빈 SampleResult (PM v3 §19 'persona 0명 매칭' UI 처리).
    sample_size <= 0 → ValueError.

    seed 결정성: random.Random(seed) 사용 (통계적 재현성 목적, 보안 용도 아님).
    """
    if sample_size <= 0:
        raise ValueError(f"sample_size must be positive, got {sample_size}")

    matched_count = len(personas)

    if matched_count == 0:
        return SampleResult(
            rows=[],
            matched_count_before_sample=0,
            sample_size=0,
            sampling_seed=seed,
        )

    if sample_size >= matched_count:
        return SampleResult(
            rows=sorted(personas, key=lambda p: p.persona_id),
            matched_count_before_sample=matched_count,
            sample_size=matched_count,
            sampling_seed=seed,
        )

    # 통계적 재현성 목적 random (보안/암호 용도 아님) — nosec B311
    rng = random.Random(seed)  # nosec B311
    selected = rng.sample(personas, sample_size)
    return SampleResult(
        rows=sorted(selected, key=lambda p: p.persona_id),
        matched_count_before_sample=matched_count,
        sample_size=sample_size,
        sampling_seed=seed,
    )


def sample_iterable_to_result(
    personas: Iterable[Persona],
    filt: PersonaFilter,
    sample_size: int,
    seed: int,
) -> SampleResult:
    """Filter and sample an iterable without materializing all personas.

    Uses reservoir sampling so memory stays bounded by sample_size. The input
    iterable may still be consumed fully when filters are active.
    """
    if sample_size <= 0:
        raise ValueError(f"sample_size must be positive, got {sample_size}")

    rng = random.Random(seed)  # nosec B311
    reservoir: list[Persona] = []
    matched_count = 0

    for persona in personas:
        if not filt.matches(persona):
            continue
        matched_count += 1
        if len(reservoir) < sample_size:
            reservoir.append(persona)
            continue
        index = rng.randrange(matched_count)
        if index < sample_size:
            reservoir[index] = persona

    if matched_count == 0:
        return SampleResult(
            rows=[],
            matched_count_before_sample=0,
            sample_size=0,
            sampling_seed=seed,
        )

    return SampleResult(
        rows=sorted(reservoir, key=lambda p: p.persona_id),
        matched_count_before_sample=matched_count,
        sample_size=min(sample_size, matched_count),
        sampling_seed=seed,
    )


def take_matching_iterable_to_result(
    personas: Iterable[Persona],
    filt: PersonaFilter,
    sample_size: int,
    seed: int,
) -> SampleResult:
    """Collect matching personas in stream order until sample_size is reached."""
    if sample_size <= 0:
        raise ValueError(f"sample_size must be positive, got {sample_size}")

    rows: list[Persona] = []
    matched_count = 0

    for persona in personas:
        if not filt.matches(persona):
            continue
        matched_count += 1
        rows.append(persona)
        if len(rows) >= sample_size:
            break

    return SampleResult(
        rows=sorted(rows, key=lambda p: p.persona_id),
        matched_count_before_sample=matched_count,
        sample_size=len(rows),
        sampling_seed=seed,
    )


def preview_first_n(rows: list[Any], n: int = 30) -> list[Any]:
    """샘플 미리보기. PM v3 §23 Phase 2 완료기준.

    rows 가 n 보다 작으면 전체 반환.
    """
    if n <= 0:
        return []
    return rows[:n]
