# k-fashion-persona Installation Guide

This app is not a hosted service. It is a local Streamlit app that runs on your machine and uses API keys that you provide.

## 1. Requirements

- Git
- Python 3.11 or newer
- `uv`
- An API key for OpenAI, Anthropic, or Gemini
- Hugging Face token if needed
- Optional KOSIS API key

`uv` installation docs:

```text
https://docs.astral.sh/uv/
```

## 2. Clone The Repository

```bash
git clone https://github.com/woooya129-ai/k-fashion-persona.git
cd k-fashion-persona
```

## 3. Install Dependencies

```bash
uv sync --all-extras --dev
```

Optional:

```bash
uv run pre-commit install
```

## 4. Run The App

```bash
uv run streamlit run src/app.py
```

Open:

```text
http://localhost:8501
```

To make the README Docs button work locally, run this in another terminal:

```bash
uv run python -m http.server 8510
```

## 5. Enter API Keys

The easiest path is to paste keys into the password fields in the app UI.

Supported key inputs:

- LLM provider API key: OpenAI / Anthropic / Google Gemini
- `HF TOKEN`: when Hugging Face access is needed
- `KOSIS API KEY`: when you enable KOSIS API refresh

KOSIS is optional when using the committed snapshot. `KOSIS API KEY` and `KOSIS statisticsData URL` are needed only when API refresh is enabled. For security, the refresh URL must use the `https://kosis.kr/openapi/statisticsData.do` path.

## 6. Environment File For Repeated Runs

Do not put real keys inside the repository. For repeated runs, keep a local environment file outside the repository.

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

Environment file example:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
HF_TOKEN=
KOSIS_API_KEY=
KOSIS_STATISTICS_DATA_URL=
```

`GOOGLE_API_KEY` is for the Gemini API key from Google AI Studio, not Vertex AI.

Do not place or commit a real `.env` file in the repository root.

## 7. Basic Workflow

1. Choose the LLM provider and model.
2. Enter the provider API key.
3. Enter `HF TOKEN` if needed.
4. Choose the KOSIS reference segment.
5. Optionally enable KOSIS API refresh and enter a URL.
6. Fill in category, price, fit, material, color, season, wearing context, style tone, target hypothesis, and product description.
7. Adjust sample size, seed, and filters.
8. Confirm estimated cost and time.
9. Press `ENTER`.
10. Download the Markdown or CSV report.

## 8. Data Location

If you use the default `NVIDIA dataset` mode, you do not need to place the raw dataset inside the repository. The app reads `nvidia/Nemotron-Personas-Korea` from Hugging Face.

For local file mode, place a `.csv` or `.parquet` file under `data/`.

Recommended location:

```text
data/raw/
```

Examples:

```text
data/raw/nemotron-personas-korea.parquet
data/raw/nemotron-personas-korea.csv
```

Enter a local path like this in the app:

```text
data/raw/nemotron-personas-korea.parquet
```

Paths outside `data/` are rejected for safety.

Optional design assets can be placed at these repository-root-relative paths:

```text
design/hero-skyblue-fabric.png
design/direction-bg.png
```

If the files are missing, the app uses built-in fallback backgrounds and logs that once.

## 9. KOSIS Statistics

The repository includes a committed public-statistics snapshot.

```text
data/public/kosis_household_context.csv
```

The snapshot is used for report and prompt economic context.

- Annualized clothing-footwear spending
- Monthly clothing-footwear spending
- Monthly household income
- Monthly disposable income
- Average household assets
- Average household debt
- Average household net assets

These values are KOSTAT/KOSIS household aggregate statistics. They do not mean an individual persona's real income, assets, or purchasing power.

To use KOSIS API refresh, create a KOSIS `statisticsData` URL and paste it into the app's `KOSIS statisticsData URL` field. The allowed path is `https://kosis.kr/openapi/statisticsData.do`.

## 10. Run Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Security and dependency checks:

```bash
uv run bandit -r src -c pyproject.toml
uv run pip-audit
uv run pre-commit run --all-files
```

Tests do not make real calls to OpenAI, Anthropic, Gemini, or Hugging Face.

## 11. Troubleshooting

### `uv` is not found

Check that `uv` is installed and included in your PATH.

### `http://localhost:8501` does not open

Check that the Streamlit process is still running. If port 8501 is already in use, Streamlit may show another local URL.

### API key errors

Check the UI field, external environment file, or OS environment variable for the key you need.

### KOSIS API refresh fails

Check `KOSIS API KEY` and `KOSIS statisticsData URL`. The URL must use the `https://kosis.kr/openapi/statisticsData.do` path. On failure, the app uses the committed public-statistics snapshot.

### Hugging Face access errors

The persona dataset may require access permission. If needed, check your Hugging Face account and token settings.
