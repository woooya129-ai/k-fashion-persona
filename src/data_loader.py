# SPDX-License-Identifier: AGPL-3.0-only
"""HF dataset / 로컬 CSV·Parquet 로딩.

PM v3 §23 Phase 2.
정책: HF dataset 원본은 git에 커밋하지 않음 (data/raw 는 gitignore), HF_TOKEN 은 저장하지 않음.
401/403/GatedRepoError 는 안내 메시지로 처리.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import Any, Literal

from src.persona_normalizer import Persona, normalize_persona
from src.secrets_loader import HF_TOKEN_VAR

# dataset_id 정규식 검증 (보안 설계 조건)
# 허용: 영문자·숫자·하이픈·언더스코어·점·슬래시 (소유자/이름 형식)
# 금지: ".." 포함 경로 (path traversal), 공백/세미콜론/특수문자
_DATASET_ID_RE = re.compile(r"^(?!.*\.\.)[\w\-./]+$")

DEFAULT_HF_DATASET_ID = "nvidia/Nemotron-Personas-Korea"
DEFAULT_SPLIT = "train"

ALLOWED_LOCAL_EXTENSIONS: tuple[str, ...] = (".csv", ".parquet")
MAX_LOCAL_FILE_BYTES: int = 500 * 1024 * 1024  # 500MB 보호 한도

# I2 해소 (current-update-review 2026-05-01): path traversal / 외부 디렉토리 접근 차단.
# 호출자가 allowed_roots 명시하지 않으면 cwd 기준 data/ 아래만 허용.
DEFAULT_ALLOWED_ROOTS: tuple[Path, ...] = (Path("data").resolve(),)

EXPECTED_COLUMNS: tuple[str, ...] = (
    "uuid",
    "professional_persona",
    "sports_persona",
    "arts_persona",
    "travel_persona",
    "culinary_persona",
    "family_persona",
    "persona",
    "cultural_background",
    "skills_and_expertise",
    "skills_and_expertise_list",
    "hobbies_and_interests",
    "hobbies_and_interests_list",
    "career_goals_and_ambitions",
    "sex",
    "age",
    "marital_status",
    "military_status",
    "family_type",
    "housing_type",
    "education_level",
    "bachelors_field",
    "occupation",
    "district",
    "province",
    "country",
)


class DatasetAccessError(RuntimeError):
    """gated / private / 401 / 403 / 네트워크 오류 통합.

    error_type: PM v3 §8.6 / §19 매트릭스 8가지 분류.
    user_message: UI 에 그대로 표시할 한국어 안내 문자열.
    missing_columns: schema_mismatch 일 때만 채움. 그 외 None.

    주의: token / 원본 에러 직렬화 금지 (런타임 데이터 정책).
    """

    def __init__(
        self,
        user_message: str,
        error_type: Literal[
            "unauthorized",
            "forbidden",
            "gated",
            "not_found",
            "network",
            "interrupted",
            "schema_mismatch",
            "invalid_path",
        ] = "network",
        missing_columns: list[str] | None = None,
    ) -> None:
        super().__init__(user_message)
        self.error_type = error_type
        self.user_message = user_message
        self.missing_columns = missing_columns


class DatasetSchemaError(ValueError):
    """필수 컬럼 누락."""


@dataclass(frozen=True)
class LoadedDataset:
    """로딩 결과 메타. 실제 raw row 는 yield 로 노출."""

    source: str  # "huggingface:..." 또는 "local:filename"
    dataset_revision: str  # HF commit SHA 또는 loader loaded_at ISO8601
    total_rows: int


def validate_columns(columns: list[str]) -> None:
    """필수 컬럼 모두 있는지 확인. 누락 시 DatasetSchemaError."""
    missing = [c for c in EXPECTED_COLUMNS if c not in columns]
    if missing:
        suffix = "..." if len(missing) > 5 else ""
        raise DatasetSchemaError(
            f"missing required columns ({len(missing)}): {missing[:5]}{suffix}"
        )


def validate_local_path(
    file_path: Path,
    allowed_roots: tuple[Path, ...] | None = None,
) -> None:
    """업로드 / 로컬 경로 검증.

    - path traversal 방지: resolve() 후 allowed_roots 하위인지 강제 검사 (I2 해소).
      symlink 도 resolve 결과 기준으로 평가.
    - 확장자 allowlist (.pkl 등 unsafe deserialization 거부 — Hard Rule §17).
    - 파일 크기 한도.

    호출자가 allowed_roots 미지정 시 DEFAULT_ALLOWED_ROOTS (cwd/data/) 만 허용.
    Streamlit UploadedFile 은 임시 디렉토리에 저장 후 그 경로를 allowed_roots 에 포함하여 호출.
    """
    file_path = Path(file_path).resolve()
    roots = tuple(Path(r).resolve() for r in (allowed_roots or DEFAULT_ALLOWED_ROOTS))

    if not file_path.is_file():
        raise FileNotFoundError(f"file not found: {file_path}")

    if not any(_is_relative_to(file_path, root) for root in roots):
        # 경로 자체는 메시지에 포함 (사용자 자기 경로 — secret 가능성 없음)
        raise ValueError(
            f"file path outside allowed roots: {file_path} (allowed: {[str(r) for r in roots]})"
        )

    suffix = file_path.suffix.lower()
    if suffix not in ALLOWED_LOCAL_EXTENSIONS:
        raise ValueError(f"unsupported extension: {suffix} (allowed: {ALLOWED_LOCAL_EXTENSIONS})")
    size = file_path.stat().st_size
    if size > MAX_LOCAL_FILE_BYTES:
        raise ValueError(f"file too large: {size} bytes > {MAX_LOCAL_FILE_BYTES} (보호 한도)")


def _is_relative_to(path: Path, base: Path) -> bool:
    """Python 3.9+ 호환 Path.is_relative_to."""
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def normalize_rows_to_personas(
    rows: Iterator[dict[str, Any]],
) -> Iterator[Persona]:
    """raw rows → Persona objects. 정규화 실패 (None 반환) row 는 skip."""
    for idx, row in enumerate(rows):
        persona = normalize_persona(row, idx)
        if persona is not None:
            yield persona


def _validate_dataset_id(dataset_id: str) -> None:
    """dataset_id 정규식 검증. 안전하지 않은 입력 거부.

    PM v3 보안 조건: dataset_id 는 `^[\\w\\-./]+$` 정규식 검증.
    """
    if not _DATASET_ID_RE.match(dataset_id):
        raise DatasetAccessError(
            "잘못된 dataset_id 형식입니다: 영문자·숫자·하이픈·언더스코어·점·슬래시만 허용됩니다.",
            error_type="invalid_path",
        )
    if dataset_id != DEFAULT_HF_DATASET_ID:
        raise DatasetAccessError(
            f"이 앱의 Hugging Face 연결은 {DEFAULT_HF_DATASET_ID} 데이터셋만 허용합니다.",
            error_type="invalid_path",
        )


def load_huggingface_dataset(
    dataset_id: str = DEFAULT_HF_DATASET_ID,
    split: str = DEFAULT_SPLIT,
    streaming: bool = True,
    revision: str | None = None,
) -> tuple[LoadedDataset, Iterator[dict[str, Any]]]:
    """HF dataset 로드.

    HF_TOKEN 은 환경변수에서 자동 로드 (huggingface_hub 표준).
    gated / private / 401 / 403 → DatasetAccessError (사용자 안내 메시지로 변환,
    provider raw error 본문은 노출하지 않음 — I1 해소).
    streaming=True: 메모리 절약 + iterator 반환 (Phase 3 worker 에서 처리).

    revision (I3 해소):
      - 명시 시 load_dataset(..., revision=revision) 으로 고정 → source_row_id 재현성 보장.
      - 미지정 시 LoadedDataset.dataset_revision = "unpinned:<HEAD ref>" 로 경고 명시.
        Phase 0 lock-in 의 재현성 요구 충족 부족 — UI 에서 사용자에게 표시 권장.

    오류 매핑 (PM v3 §8.6):
      401 / RepositoryNotFoundError(gated) → unauthorized
      403 / PermissionError              → forbidden
      GatedRepoError                     → gated
      DatasetNotFound / RepositoryNotFoundError → not_found
      ConnectionError / TimeoutError     → network
      그 외 예외                          → network (raw error 본문 노출 금지)
    """
    _validate_dataset_id(dataset_id)

    try:
        from datasets import load_dataset  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DatasetAccessError(
            "datasets 패키지 미설치. uv add datasets 후 재실행.",
            error_type="network",
        ) from exc

    token = os.environ.get(HF_TOKEN_VAR) or None  # 명시적 None (datasets 권장)

    try:
        ds = load_dataset(
            dataset_id,
            split=split,
            streaming=streaming,
            token=token,
            revision=revision,
        )
    except Exception as exc:
        # I1 해소: provider raw error 본문 노출 금지. exception-class 기반 분류.
        exc_type_name = type(exc).__name__
        exc_msg_lower = str(exc).lower()

        # GatedRepoError (huggingface_hub)
        if exc_type_name == "GatedRepoError":
            raise DatasetAccessError(
                "접근 요청이 필요한 데이터셋입니다. "
                "Hugging Face 데이터셋 페이지에서 접근 신청 후 재시도하세요.",
                error_type="gated",
            ) from exc

        # 401 Unauthorized — 문자열 기반.
        # 주의: HF 가 인증 실패 시 RepositoryNotFoundError 로 마스킹하는 경우가 있어
        # not_found 분기보다 먼저 401 키워드를 확인한다.
        if "401" in exc_msg_lower or "unauthorized" in exc_msg_lower:
            raise DatasetAccessError(
                "Hugging Face 토큰이 유효하지 않습니다. "
                "~/secrets/k-fashion/.env 의 HF_TOKEN 을 확인하세요.",
                error_type="unauthorized",
            ) from exc

        # DatasetNotFoundError / RepositoryNotFoundError (not_found)
        if exc_type_name in ("DatasetNotFoundError", "RepositoryNotFoundError"):
            raise DatasetAccessError(
                "데이터셋을 찾을 수 없습니다. dataset_id 를 확인하세요.",
                error_type="not_found",
            ) from exc

        # 403 Forbidden
        if "403" in exc_msg_lower or "forbidden" in exc_msg_lower or "permission" in exc_msg_lower:
            raise DatasetAccessError(
                "데이터셋 접근 권한이 없습니다. "
                "Hugging Face 데이터셋 페이지에서 접근 승인 또는 약관 동의가 필요합니다.",
                error_type="forbidden",
            ) from exc

        # ConnectionError / TimeoutError → network
        if isinstance(exc, ConnectionError | TimeoutError) or any(
            k in exc_msg_lower for k in ("connection", "timeout", "network", "unreachable")
        ):
            raise DatasetAccessError(
                "데이터셋 다운로드에 실패했습니다. 네트워크 상태를 확인 후 재시도하세요.",
                error_type="network",
            ) from exc

        # interrupted (KeyboardInterrupt 등은 여기까지 도달하지 않음 — 그대로 전파)
        # 그 외: 원인 불명 → network 분류, raw error 본문 노출 금지.
        raise DatasetAccessError(
            "데이터셋 다운로드에 실패했습니다. 네트워크 상태를 확인 후 재시도하세요.",
            error_type="network",
        ) from exc

    columns = list(ds.column_names) if hasattr(ds, "column_names") and ds.column_names else []
    if columns:
        try:
            validate_columns(columns)
        except DatasetSchemaError as exc:
            missing = [c for c in EXPECTED_COLUMNS if c not in columns]
            raise DatasetAccessError(
                f"필요한 컬럼이 없습니다: {missing[:5]}{'...' if len(missing) > 5 else ''}",
                error_type="schema_mismatch",
                missing_columns=missing,
            ) from exc

    # I3 해소: revision 명시 / 미명시 구분.
    # UI 에서 unpinned 경고 표시 권장 (재현성 약화).
    rev_str = f"pinned:{revision}" if revision else "unpinned:HEAD"

    total = -1  # streaming 시 unknown
    if not streaming and hasattr(ds, "__len__"):
        total = len(ds)

    return (
        LoadedDataset(
            source=f"huggingface:{dataset_id}",
            dataset_revision=rev_str,
            total_rows=total,
        ),
        iter(ds),
    )


def load_local_file(file_path: Path) -> tuple[LoadedDataset, Iterator[dict[str, Any]]]:
    """로컬 CSV / Parquet 로드. pandas 의존.

    validate_local_path 는 invalid_path / FileNotFoundError 를 유지하면서
    DatasetAccessError(error_type="invalid_path") 로 래핑.
    DatasetSchemaError 는 DatasetAccessError(error_type="schema_mismatch") 로 래핑.
    """
    # invalid_path / path traversal 검증
    try:
        validate_local_path(file_path)
    except FileNotFoundError as exc:
        raise DatasetAccessError(
            f"파일을 찾을 수 없습니다: {Path(file_path).name}",
            error_type="invalid_path",
        ) from exc
    except ValueError as exc:
        raise DatasetAccessError(
            str(exc),
            error_type="invalid_path",
        ) from exc

    file_path = Path(file_path)

    try:
        import pandas as pd  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DatasetAccessError(
            "pandas 미설치. uv add pandas 후 재실행.",
            error_type="network",
        ) from exc

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        raise DatasetAccessError(
            f"지원하지 않는 파일 형식입니다: {suffix}",
            error_type="invalid_path",
        )

    try:
        validate_columns(list(df.columns))
    except DatasetSchemaError as exc:
        missing = [c for c in EXPECTED_COLUMNS if c not in list(df.columns)]
        raise DatasetAccessError(
            f"필요한 컬럼이 없습니다: {missing[:5]}{'...' if len(missing) > 5 else ''}",
            error_type="schema_mismatch",
            missing_columns=missing,
        ) from exc

    from datetime import datetime

    loaded_at = datetime.now(UTC).isoformat()
    rows = (row.to_dict() for _, row in df.iterrows())

    return (
        LoadedDataset(
            source=f"local:{file_path.name}",
            dataset_revision=f"loaded_at:{loaded_at}",
            total_rows=len(df),
        ),
        rows,
    )
