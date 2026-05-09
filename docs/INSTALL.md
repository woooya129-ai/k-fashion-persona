# k-fashion-persona 설치 및 실행 가이드

이 앱은 hosted 서비스가 아니라 로컬 Streamlit 앱입니다. 사용자는 자신의 컴퓨터에서 앱을 실행하고, 자신이 보유한 LLM provider API key를 사용합니다.

## 1. 필요 조건

- Git
- Python 3.11 이상
- `uv`
- OpenAI, Anthropic, Gemini 중 사용할 provider API key
- 필요 시 Hugging Face token
- 선택 사항: KOSIS API key

`uv` 설치 문서:

```text
https://docs.astral.sh/uv/
```

## 2. 저장소 받기

```bash
git clone https://github.com/woooya129-ai/k-fashion-persona.git
cd k-fashion-persona
```

## 3. 의존성 설치

```bash
uv sync --all-extras --dev
```

선택 사항:

```bash
uv run pre-commit install
```

## 4. 앱 실행

```bash
uv run streamlit run src/app.py
```

브라우저에서 엽니다.

```text
http://localhost:8501
```

README의 Docs 버튼까지 로컬에서 열고 싶으면 다른 터미널에서 실행합니다.

```bash
uv run python -m http.server 8510
```

## 5. API Key 입력

가장 쉬운 방식은 앱 화면의 password 입력칸에 key를 붙여넣는 것입니다.

입력 가능한 key:

- LLM provider API key: OpenAI / Anthropic / Google Gemini
- `HF TOKEN`: Hugging Face 접근이 필요할 때
- `KOSIS API KEY`: KOSIS 통계자료 API 갱신을 사용할 때

KOSIS는 기본 스냅샷만 사용할 경우 key가 없어도 됩니다. API 갱신을 켤 때만 `KOSIS API KEY`와 `KOSIS statisticsData URL`이 필요합니다.

## 6. 반복 실행용 환경 파일

실제 key를 저장소 안에 넣지 마세요. 반복 실행이 필요하면 저장소 밖에 환경 파일을 둡니다.

### macOS / Linux

```bash
mkdir -p ~/secrets/k-fashion
cp .env.example ~/secrets/k-fashion/.env
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME\secrets\k-fashion"
Copy-Item .env.example "$HOME\secrets\k-fashion\.env"
```

환경 파일 예시:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
HF_TOKEN=
KOSIS_API_KEY=
KOSIS_STATISTICS_DATA_URL=
```

`GOOGLE_API_KEY`는 Google AI Studio의 Gemini API key 기준입니다. Vertex AI key가 아닙니다.

저장소 root에 실제 `.env` 파일을 두거나 commit하지 마세요.

## 7. 기본 사용 순서

1. LLM provider와 model을 선택합니다.
2. provider API key를 입력합니다.
3. 필요하면 `HF TOKEN`을 입력합니다.
4. KOSIS 기준 계층을 선택합니다.
5. 필요하면 KOSIS API 갱신을 켜고 URL을 입력합니다.
6. 제품 카드에 카테고리, 가격, 핏, 소재, 컬러, 시즌, 착용 상황, 스타일 톤, 타깃 가설, 제품 설명을 입력합니다.
7. sample size, seed, 필터를 조정합니다.
8. 예상 비용과 시간을 확인합니다.
9. `ENTER`를 누릅니다.
10. Markdown 또는 CSV 리포트를 내려받습니다.

## 8. 데이터 위치

기본값인 `NVIDIA dataset` 모드를 쓰면 원본 데이터셋을 저장소에 직접 넣지 않아도 됩니다. 앱이 Hugging Face의 `nvidia/Nemotron-Personas-Korea`를 읽습니다.

로컬 파일 모드에서는 `.csv` 또는 `.parquet` 파일을 저장소의 `data/` 하위에 둬야 합니다.

권장 위치:

```text
data/raw/
```

예시:

```text
data/raw/nemotron-personas-korea.parquet
data/raw/nemotron-personas-korea.csv
```

앱의 `로컬 파일 경로` 입력칸에는 다음처럼 입력합니다.

```text
data/raw/nemotron-personas-korea.parquet
```

`data/` 바깥 경로는 보안상 거부됩니다.

## 9. KOSIS 통계

저장소에는 공개 통계 스냅샷이 포함됩니다.

```text
data/public/kosis_household_context.csv
```

이 스냅샷은 리포트와 프롬프트의 경제 맥락에 사용됩니다.

- 연간 환산 의류·신발 지출
- 월평균 의류·신발 지출
- 월평균 가구소득
- 월평균 처분가능소득
- 평균 가구자산
- 평균 가구부채
- 평균 가구순자산

이 값들은 KOSTAT/KOSIS 가구 단위 집계 통계입니다. 개별 페르소나의 실제 소득, 자산, 구매력을 뜻하지 않습니다.

KOSIS API 갱신을 쓰려면 KOSIS에서 `statisticsData` URL을 만든 뒤 앱의 `KOSIS statisticsData URL` 입력칸에 넣습니다.

## 10. 테스트 실행

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

보안/의존성 검사:

```bash
uv run bandit -r src -c pyproject.toml
uv run pip-audit
uv run pre-commit run --all-files
```

테스트는 실제 OpenAI, Anthropic, Gemini, Hugging Face API를 호출하지 않습니다.

## 11. 문제 해결

### `uv` 명령을 찾을 수 없음

`uv`가 설치되어 있는지 확인하고, 설치 경로가 PATH에 포함되어 있는지 확인하세요.

### `http://localhost:8501`이 열리지 않음

Streamlit 실행 명령이 아직 실행 중인지 확인하세요. 포트가 이미 사용 중이면 Streamlit이 다른 포트를 안내할 수 있습니다.

### API key 오류가 남

화면 입력칸, 저장소 밖 환경 파일, OS 환경변수 중 하나에 필요한 key가 설정되어 있는지 확인하세요.

### KOSIS API 갱신이 실패함

`KOSIS API KEY`와 `KOSIS statisticsData URL`을 확인하세요. 실패 시 앱은 저장소의 공개 통계 스냅샷을 사용합니다.

### Hugging Face 접근 오류가 남

사용하는 persona dataset이 접근 권한을 요구할 수 있습니다. 필요한 경우 Hugging Face 계정과 token 설정을 확인하세요.
