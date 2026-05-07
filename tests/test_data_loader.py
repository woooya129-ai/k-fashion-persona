"""src/data_loader.py 테스트.

실제 HF 호출 / 실제 파일 읽기는 안 함 (Hard Rule §18 / security policy: no_network).
validate_columns / validate_local_path / normalize_rows_to_personas 만 테스트.
load_huggingface_dataset / load_local_file 는 monkeypatch 기반 테스트.
"""

import sys
from pathlib import Path

import pytest

from src.data_loader import (
    ALLOWED_LOCAL_EXTENSIONS,
    EXPECTED_COLUMNS,
    MAX_LOCAL_FILE_BYTES,
    DatasetAccessError,
    DatasetSchemaError,
    normalize_rows_to_personas,
    validate_columns,
    validate_local_path,
)
from tests.fixtures.mock_hf_rows import MOCK_HF_ROWS
from tests.fixtures.mock_personas import ALL_MOCK_PERSONAS

pytestmark = pytest.mark.no_network


class TestValidateColumns:
    def test_all_present(self):
        validate_columns(list(EXPECTED_COLUMNS))

    def test_extra_columns_ok(self):
        validate_columns(list(EXPECTED_COLUMNS) + ["bonus", "extra"])

    def test_missing_one_raises(self):
        cols = [c for c in EXPECTED_COLUMNS if c != "persona"]
        with pytest.raises(DatasetSchemaError):
            validate_columns(cols)

    def test_missing_uuid_raises(self):
        cols = [c for c in EXPECTED_COLUMNS if c != "uuid"]
        with pytest.raises(DatasetSchemaError):
            validate_columns(cols)

    def test_empty_columns_raises(self):
        with pytest.raises(DatasetSchemaError):
            validate_columns([])

    def test_count_is_26(self):
        # lock-in §1.1 검증 결과 = 26개 (DISCUSS-W4 dataset 검증 완료)
        assert len(EXPECTED_COLUMNS) == 26


class TestValidateLocalPath:
    def test_csv_extension_ok(self, tmp_path: Path):
        p = tmp_path / "data.csv"
        p.write_text("a,b,c\n", encoding="utf-8")
        validate_local_path(p, allowed_roots=(tmp_path,))

    def test_parquet_extension_ok(self, tmp_path: Path):
        p = tmp_path / "data.parquet"
        p.write_bytes(b"PAR1")
        validate_local_path(p, allowed_roots=(tmp_path,))

    def test_nonexistent_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            validate_local_path(tmp_path / "missing.csv", allowed_roots=(tmp_path,))

    def test_disallowed_extension_raises(self, tmp_path: Path):
        p = tmp_path / "data.json"
        p.write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match="unsupported extension"):
            validate_local_path(p, allowed_roots=(tmp_path,))

    def test_pickle_extension_raises(self, tmp_path: Path):
        # Hard Rule §17: pickle 사용 금지
        p = tmp_path / "data.pkl"
        p.write_bytes(b"x")
        with pytest.raises(ValueError, match="unsupported"):
            validate_local_path(p, allowed_roots=(tmp_path,))

    def test_oversize_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        import stat as stat_module

        p = tmp_path / "data.csv"
        p.write_text("a\n", encoding="utf-8")
        # monkeypatch 전에 resolve 결과를 캐시 — fake_stat 내부 비교가
        # Path.resolve() 를 호출하면 다시 monkeypatched stat 으로 재진입해 무한재귀.
        p_resolved = p.resolve()
        original_stat = Path.stat

        class FakeStat:
            st_size = MAX_LOCAL_FILE_BYTES + 1
            # is_file() 이 S_ISREG(st_mode) 를 검사하므로 정규파일 비트 필요.
            st_mode = stat_module.S_IFREG | 0o644

        def fake_stat(self, *args, **kwargs):
            if self == p_resolved:
                return FakeStat()
            return original_stat(self, *args, **kwargs)

        monkeypatch.setattr(Path, "stat", fake_stat)
        with pytest.raises(ValueError, match="too large"):
            validate_local_path(p, allowed_roots=(tmp_path,))

    def test_outside_allowed_roots_rejected(self, tmp_path: Path):
        """I2 해소 검증: allowed_roots 밖 파일 거부."""
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "data.csv"
        outside_file.write_text("a\n", encoding="utf-8")

        allowed = tmp_path / "allowed"
        allowed.mkdir()

        with pytest.raises(ValueError, match="outside allowed roots"):
            validate_local_path(outside_file, allowed_roots=(allowed,))

    def test_path_traversal_rejected(self, tmp_path: Path):
        """I2 해소: '../' path traversal 차단."""
        allowed = tmp_path / "allowed"
        allowed.mkdir()
        sibling = tmp_path / "sibling.csv"
        sibling.write_text("a\n", encoding="utf-8")

        traversal = allowed / ".." / "sibling.csv"
        with pytest.raises(ValueError, match="outside allowed roots"):
            validate_local_path(traversal, allowed_roots=(allowed,))

    def test_default_allowed_roots_uses_data_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """allowed_roots 미지정 시 DEFAULT_ALLOWED_ROOTS (cwd/data) 적용."""
        monkeypatch.chdir(tmp_path)
        outside = tmp_path / "x.csv"
        outside.write_text("a\n", encoding="utf-8")
        with pytest.raises(ValueError, match="outside allowed roots"):
            validate_local_path(outside)


class TestNormalizeRowsToPersonas:
    def test_all_mock_personas_yield(self):
        personas = list(normalize_rows_to_personas(iter(ALL_MOCK_PERSONAS)))
        assert len(personas) == len(ALL_MOCK_PERSONAS)

    def test_invalid_rows_skipped(self):
        rows = [
            ALL_MOCK_PERSONAS[0],
            {"uuid": "", "age": 1, "sex": "F", "persona": "x"},  # empty uuid → skip
            ALL_MOCK_PERSONAS[1],
        ]
        personas = list(normalize_rows_to_personas(iter(rows)))
        assert len(personas) == 2

    def test_source_row_id_assigned(self):
        rows = list(ALL_MOCK_PERSONAS)
        personas = list(normalize_rows_to_personas(iter(rows)))
        assert [p.source_row_id for p in personas] == list(range(len(rows)))


class TestModuleConstants:
    def test_allowed_extensions(self):
        assert ".csv" in ALLOWED_LOCAL_EXTENSIONS
        assert ".parquet" in ALLOWED_LOCAL_EXTENSIONS
        assert ".pkl" not in ALLOWED_LOCAL_EXTENSIONS
        assert ".json" not in ALLOWED_LOCAL_EXTENSIONS

    def test_max_file_bytes_reasonable(self):
        # 100MB ~ 1GB 사이가 합리적 (HF dataset 1행씩 streaming 권장)
        assert 100 * 1024 * 1024 <= MAX_LOCAL_FILE_BYTES <= 1024 * 1024 * 1024


# ---------------------------------------------------------------------------
# DatasetAccessError 속성 검증
# ---------------------------------------------------------------------------


class TestDatasetAccessError:
    """DatasetAccessError 8가지 error_type + user_message + missing_columns 검증."""

    def test_default_error_type_is_network(self):
        err = DatasetAccessError("테스트 오류")
        assert err.error_type == "network"
        assert err.user_message == "테스트 오류"
        assert err.missing_columns is None

    def test_all_eight_error_types_accepted(self):
        types = [
            "unauthorized",
            "forbidden",
            "gated",
            "not_found",
            "network",
            "interrupted",
            "schema_mismatch",
            "invalid_path",
        ]
        for etype in types:
            err = DatasetAccessError("메시지", error_type=etype)  # type: ignore[arg-type]
            assert err.error_type == etype

    def test_missing_columns_set_for_schema_mismatch(self):
        err = DatasetAccessError(
            "컬럼 누락",
            error_type="schema_mismatch",
            missing_columns=["uuid", "age"],
        )
        assert err.missing_columns == ["uuid", "age"]

    def test_is_runtime_error_subclass(self):
        err = DatasetAccessError("오류")
        assert isinstance(err, RuntimeError)

    def test_str_is_user_message(self):
        err = DatasetAccessError("사용자 안내 메시지")
        assert "사용자 안내 메시지" in str(err)


# ---------------------------------------------------------------------------
# load_huggingface_dataset — monkeypatch 기반 (실제 HF 호출 없음)
# ---------------------------------------------------------------------------


def _make_fake_dataset(rows: list[dict], column_names: list[str] | None = None):
    """load_dataset 이 반환하는 가짜 iterable 객체."""

    class FakeDS:
        def __init__(self) -> None:
            self.column_names = column_names or (list(rows[0].keys()) if rows else [])

        def __iter__(self):
            return iter(rows)

        def __len__(self):
            return len(rows)

    return FakeDS()


class TestLoadHuggingfaceDataset:
    """monkeypatch 로 datasets.load_dataset 를 fake 주입하는 테스트."""

    def _patch_load_dataset(self, monkeypatch, fake_fn):
        """sys.modules["datasets"] 에 가짜 모듈 주입."""

        class FakeDatasets:
            @staticmethod
            def load_dataset(*args, **kwargs):
                return fake_fn(*args, **kwargs)

        monkeypatch.setitem(sys.modules, "datasets", FakeDatasets)

    # 1. 정상 26컬럼 → LoadedDataset 반환
    def test_happy_path_returns_loaded_dataset(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        def fake_load(*args, **kwargs):
            return _make_fake_dataset(MOCK_HF_ROWS)

        self._patch_load_dataset(monkeypatch, fake_load)

        meta, rows_iter = load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert meta.source == "huggingface:nvidia/Nemotron-Personas-Korea"
        assert "unpinned" in meta.dataset_revision or "pinned" in meta.dataset_revision
        assert meta.dataset_split == "train"

    # 2. revision 고정 시 pinned: 반영
    def test_revision_pinned_reflected(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        def fake_load(*args, **kwargs):
            return _make_fake_dataset(MOCK_HF_ROWS)

        self._patch_load_dataset(monkeypatch, fake_load)

        meta, _ = load_huggingface_dataset("nvidia/Nemotron-Personas-Korea", revision="abc123")
        assert meta.dataset_revision == "pinned:abc123"
        assert meta.dataset_split == "train"

    # 3. GatedRepoError → error_type="gated"
    def test_gated_repo_error_maps_to_gated(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        class GatedRepoError(Exception):
            pass

        def fake_load(*args, **kwargs):
            raise GatedRepoError("gated")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "gated"
        assert "접근 요청" in exc_info.value.user_message

    # 4. DatasetNotFoundError → error_type="not_found"
    def test_dataset_not_found_maps_to_not_found(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        class DatasetNotFoundError(Exception):
            pass

        def fake_load(*args, **kwargs):
            raise DatasetNotFoundError("not found")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "not_found"
        assert "찾을 수 없습니다" in exc_info.value.user_message

    # 5. RepositoryNotFoundError → error_type="not_found"
    def test_repository_not_found_maps_to_not_found(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        class RepositoryNotFoundError(Exception):
            pass

        def fake_load(*args, **kwargs):
            raise RepositoryNotFoundError("repo not found")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "not_found"

    # 5b. RepositoryNotFoundError + "401" 메시지 → unauthorized 우선
    # HF 가 인증 실패를 RepositoryNotFoundError 로 마스킹하는 케이스 방어.
    def test_repository_not_found_with_401_maps_to_unauthorized(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        class RepositoryNotFoundError(Exception):
            pass

        def fake_load(*args, **kwargs):
            raise RepositoryNotFoundError(
                "401 Client Error: Unauthorized for url: https://huggingface.co/api/..."
            )

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "unauthorized"
        assert "토큰" in exc_info.value.user_message

    # 6. 401 문자열 → error_type="unauthorized"
    def test_401_string_maps_to_unauthorized(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        def fake_load(*args, **kwargs):
            raise RuntimeError("HTTP Error 401: unauthorized token")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "unauthorized"
        assert "토큰" in exc_info.value.user_message

    # 7. 403 문자열 → error_type="forbidden"
    def test_403_string_maps_to_forbidden(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        def fake_load(*args, **kwargs):
            raise RuntimeError("HTTP Error 403 forbidden")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "forbidden"
        assert "접근 권한" in exc_info.value.user_message

    # 8. ConnectionError → error_type="network"
    def test_connection_error_maps_to_network(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        def fake_load(*args, **kwargs):
            raise ConnectionError("connection refused")

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "network"
        assert "다운로드" in exc_info.value.user_message

    # 9. 25컬럼 (1개 누락) → error_type="schema_mismatch" + missing_columns
    def test_25_columns_raises_schema_mismatch(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        # uuid 컬럼 제거한 25컬럼 rows
        partial_cols = [c for c in EXPECTED_COLUMNS if c != "uuid"]
        short_rows = [{c: "x" for c in partial_cols}]

        def fake_load(*args, **kwargs):
            return _make_fake_dataset(short_rows, column_names=partial_cols)

        self._patch_load_dataset(monkeypatch, fake_load)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")
        assert exc_info.value.error_type == "schema_mismatch"
        assert exc_info.value.missing_columns is not None
        assert "uuid" in exc_info.value.missing_columns

    # 10. dataset_id "../etc/passwd" → invalid_path (정규식 거부)
    def test_invalid_dataset_id_raises_invalid_path(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("../etc/passwd")
        assert exc_info.value.error_type == "invalid_path"

    # 11. dataset_id 에 특수문자 포함 → invalid_path
    def test_dataset_id_with_special_chars_raises(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/data;rm -rf /")
        assert exc_info.value.error_type == "invalid_path"

    def test_non_default_hf_dataset_is_rejected(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("otherorg/other-dataset")
        assert exc_info.value.error_type == "invalid_path"
        assert "nvidia/Nemotron-Personas-Korea" in exc_info.value.user_message

    # 12. HF_TOKEN 이 응답/repr 에 노출되지 않음 (보안 검증)
    def test_hf_token_not_leaked_in_error(self, monkeypatch):
        from src.data_loader import load_huggingface_dataset

        fake_token = "hf_FAKE_TOKEN_FOR_TESTING_ONLY_AAABBB"

        def fake_load(*args, **kwargs):
            raise RuntimeError("Some error without token info")

        self._patch_load_dataset(monkeypatch, fake_load)
        monkeypatch.setenv("HF_TOKEN", fake_token)

        with pytest.raises(DatasetAccessError) as exc_info:
            load_huggingface_dataset("nvidia/Nemotron-Personas-Korea")

        # 토큰 문자열이 user_message 또는 str(error) 에 포함되면 안 됨
        assert fake_token not in exc_info.value.user_message
        assert fake_token not in str(exc_info.value)


# ---------------------------------------------------------------------------
# load_local_file — DatasetAccessError 래핑 검증
# ---------------------------------------------------------------------------


class TestLoadLocalFileErrors:
    """load_local_file 이 invalid_path / schema_mismatch 를 DatasetAccessError 로 래핑."""

    def test_nonexistent_file_raises_invalid_path(self, tmp_path: Path, monkeypatch):
        from src.data_loader import load_local_file

        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        with pytest.raises(DatasetAccessError) as exc_info:
            load_local_file(data_dir / "missing.csv")
        assert exc_info.value.error_type == "invalid_path"

    def test_wrong_extension_raises_invalid_path(self, tmp_path: Path):
        from src.data_loader import load_local_file

        p = tmp_path / "data.txt"
        p.write_text("hello\n", encoding="utf-8")

        with pytest.raises(DatasetAccessError) as exc_info:
            load_local_file(p)
        assert exc_info.value.error_type == "invalid_path"

    def test_path_traversal_raises_invalid_path(self, tmp_path: Path, monkeypatch):
        from src.data_loader import load_local_file

        monkeypatch.chdir(tmp_path)
        allowed = tmp_path / "data"
        allowed.mkdir()
        sibling = tmp_path / "secret.csv"
        sibling.write_text("a\n", encoding="utf-8")

        with pytest.raises(DatasetAccessError) as exc_info:
            load_local_file(allowed / ".." / "secret.csv")
        assert exc_info.value.error_type == "invalid_path"

    def test_missing_columns_raises_schema_mismatch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """필수 컬럼 누락 CSV (allowed_roots 포함) → schema_mismatch DatasetAccessError."""
        pytest.importorskip("pandas")

        import src.data_loader as dl_module

        monkeypatch.setattr(dl_module, "DEFAULT_ALLOWED_ROOTS", (tmp_path,))

        p = tmp_path / "bad.csv"
        # only 2 columns — all 26 required ones missing
        p.write_text("col_a,col_b\nval1,val2\n", encoding="utf-8")

        from src.data_loader import load_local_file

        with pytest.raises(DatasetAccessError) as exc_info:
            load_local_file(p)
        assert exc_info.value.error_type == "schema_mismatch"
        assert exc_info.value.missing_columns is not None
        assert len(exc_info.value.missing_columns) > 0

    def test_mock_csv_fixture_loads_ok(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """tests/fixtures/mock_local_csv.csv 정상 로드."""
        pytest.importorskip("pandas")

        import shutil

        import src.data_loader as dl_module

        fixture_csv = Path(__file__).parent / "fixtures" / "mock_local_csv.csv"
        dest = tmp_path / "mock_local_csv.csv"
        shutil.copy(fixture_csv, dest)

        monkeypatch.setattr(dl_module, "DEFAULT_ALLOWED_ROOTS", (tmp_path,))

        from src.data_loader import load_local_file

        meta, rows_iter = load_local_file(dest)
        rows = list(rows_iter)
        assert meta.source == "local:mock_local_csv.csv"
        assert meta.dataset_split is None
        assert len(rows) == 5

    def test_mock_parquet_fixture_loads_ok(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """mock_local_parquet.write_mock_parquet 헬퍼로 생성한 parquet 정상 로드."""
        pytest.importorskip("pandas")
        pytest.importorskip("pyarrow")

        from tests.fixtures.mock_local_parquet import write_mock_parquet

        parquet_path = write_mock_parquet(tmp_path)

        import src.data_loader as dl_module

        monkeypatch.setattr(dl_module, "DEFAULT_ALLOWED_ROOTS", (tmp_path,))

        from src.data_loader import load_local_file

        meta, rows_iter = load_local_file(parquet_path)
        rows = list(rows_iter)
        assert meta.source == "local:mock_data.parquet"
        assert len(rows) == 5
