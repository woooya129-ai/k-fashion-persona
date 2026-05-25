# k-fashion-persona

## Check K-fashion Concepts With AI Personas First

[![Version](https://img.shields.io/badge/version-0.7.1-0F766E)](../pyproject.toml)
[![HF Dataset](https://img.shields.io/badge/HF-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
[![GitHub](https://img.shields.io/badge/GitHub-k--fashion--persona-181717?logo=github&logoColor=white)](https://github.com/woooya129-ai/k-fashion-persona)
[![HF Space](https://img.shields.io/badge/HF%20Space-k--fashion--persona-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/w00ya/k-fashion-persona)
[![Live App](https://img.shields.io/badge/Live%20App-hf.space-0F766E)](https://w00ya-k-fashion-persona.hf.space)
[![Docs](https://img.shields.io/badge/Docs-INSTALL--ENG-2563EB?logo=readthedocs&logoColor=white)](INSTALL-ENG.md)
[![Korean README](https://img.shields.io/badge/README-Korean-2563EB)](../README.md)
[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-0F766E.svg)](../LICENSE)

![k-fashion-persona overview](assets/k-fashion-persona-images.jpeg)

`k-fashion-persona` is a local-first Streamlit tool for checking Korean fashion product concepts before launch or formal research. Enter a product card and persona filters, then get a Markdown/CSV report with interest reasons, hesitation points, price burden, and fashion risk signals.

It is not a real purchase-rate, sales, or market-share prediction service. Use it to narrow hypotheses before surveys, interviews, and sales-data analysis.

## At A Glance

| Item | Details |
|---|---|
| Input | Category, price, fit, material, color, season, wearing context, style tone, target hypothesis, product description |
| Panel | Synthetic personas from NVIDIA Nemotron-Personas-Korea |
| Filters | Age, sex, province, occupation, seed, sample size |
| Output | Reaction distribution, interest score, reasons, concerns, price burden, representative card, Markdown/CSV |
| Presets | FAST 50, BALANCE 100, HIGH 300, MAX 1000 personas |
| Advanced | User-entered sample sizes are allowed |

![main screen](assets/kfashionpersona-screenshot-03.webp)

![result screen](assets/kfashionpersona-screenshot-04.webp)

## Runtime Model

- UI, dataset filtering, sampling, prompt construction, SQLite cache, and Markdown/CSV report generation run locally on the user's machine.
- Streamlit API mode sends prompts to the selected provider API server.
- Agent Pack mode exports prompt files and lets your Codex or Claude Code CLI evaluate them.
- The app does not save API keys. UI-entered keys are used only for the current Streamlit session.
- LLM API endpoints are limited to `api_base_url` hosts in `config/pricing_config.yaml`. Editing that file changes the allowed host set, so review it before shared deployment.
- The public HF Space is deployed with `KFPS_REQUIRE_USER_PROVIDER_KEY=1`. It does not use shared owner LLM provider API keys. Visitors must enter their own provider key.

## Installation

Requirements:

- Git
- Python 3.11 or newer
- `uv`
- An API key for your chosen LLM provider or a signed-in Codex/Claude Code CLI
- Hugging Face token if needed

Install:

```bash
git clone https://github.com/woooya129-ai/k-fashion-persona.git
cd k-fashion-persona
uv sync --all-extras --dev
```

Full setup guide: [docs/INSTALL-ENG.md](INSTALL-ENG.md)

## Quick Start

```bash
uv run streamlit run src/app.py
```

Open:

```text
http://localhost:8501
```

## Standard Use

1. Run the Streamlit app.
2. Choose a provider and model.
3. Enter the provider API key.
4. Fill in the product card.
5. Adjust sample size, seed, and persona filters.
6. Check estimated cost and time.
7. Press `ENTER`, then download Markdown or CSV.

For repeated local runs, keep keys in an environment file outside the repository or in OS environment variables. Do not place or commit a real `.env` file in the repository root.

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
QWEN_API_KEY=
HF_TOKEN=
KOSIS_API_KEY=
DATAGOKR_SERVICE_KEY=
KOSIS_STATISTICS_DATA_URL=
MOIS_POPULATION_API_URL=
```

## Codex / Claude Code Subscription Mode

Codex and Claude Code subscription users can use `Agent Pack` mode without turning those tools into direct in-app API providers. The flow is offline: `export -> CLI run -> import`.

Codex CLI:

```powershell
npm install -g @openai/codex
codex
```

Claude Code:

```powershell
irm https://claude.ai/install.ps1 | iex
claude
```

Create an Agent Pack:

```powershell
uv run python -m src.agent_bridge export --concept examples/agent_bridge_concept.example.json --out outputs/agent-pack-demo --sample-size 50 --audience unisex
```

Run with Codex, then import:

```powershell
powershell -ExecutionPolicy Bypass -File outputs\agent-pack-demo\commands\run-codex.ps1
uv run python -m src.agent_bridge import --pack outputs\agent-pack-demo --results outputs\agent-pack-demo\results\codex --out outputs\agent-report-codex
```

Run with Claude Code, then import:

```powershell
powershell -ExecutionPolicy Bypass -File outputs\agent-pack-demo\commands\run-claude.ps1
uv run python -m src.agent_bridge import --pack outputs\agent-pack-demo --results outputs\agent-pack-demo\results\claude --out outputs\agent-report-claude
```

Notes:

- A 50-persona run makes 50 CLI calls. Start with `--sample-size 5` or `--sample-size 10`.
- Claude subscription users should use the default `run-claude.ps1`. `KFPS_CLAUDE_BARE=1` is for API-key or auth-helper automation.
- Import writes `agent-report.md`, `agent-report.csv`, and `normalized-results.jsonl`.
- Codex docs: [OpenAI Codex CLI](https://developers.openai.com/codex/cli)
- Claude docs: [Claude Code setup](https://code.claude.com/docs/en/setup)

## Data And Statistics

- Default dataset: [NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
- Dataset type: synthetic Korean-context personas, not real-person data
- Dataset license: CC BY 4.0 attribution
- Size: officially listed as 1M records, 7M persona descriptions, 26 fields, and about 1.98GB of Parquet data
- Default loading: Hugging Face `datasets` streaming
- Default scan: up to 3000 rows sequentially per run to fill matching personas


## Recommended Specs

| Item | Minimum | Recommended |
|---|---:|---:|
| CPU | 2+ cores | 4+ cores |
| RAM | 8GB | 16GB+ |
| Disk space | 5GB+ free | 10-20GB+ free |
| GPU | Not required | Not required |
| Network | Required for HF dataset loading and LLM API calls | Stable broadband recommended |

Large samples usually increase LLM API cost and runtime before RAM becomes the bottleneck.

## Interpreting Results

Appropriate use:

- Drafting survey questions before formal research
- Finding weak points in product descriptions
- Reviewing price, material, fit, and styling risks
- Comparing early concept candidates

Inappropriate use:

- Real purchase-rate prediction
- Real sales prediction
- Market-share prediction
- Replacement for real consumer research
- Sole basis for launch, production, or inventory decisions

## Limits

- Synthetic persona reactions can differ from real buying behavior.
- The dataset is not built specifically for fashion purchase research.
- Images, lookbooks, fit photos, and body measurements are not included by default.
- KOSIS/KOSTAT values are household-level aggregate statistics, and MOIS values are resident-registration aggregate statistics. They are not individual persona economics or purchasing power.
- Final decisions should combine real research, sales data, and expert review.

## License And Attribution

- Code license: GNU AGPL-3.0-only
- Persona dataset: NVIDIA Nemotron-Personas-Korea
- Dataset license: CC BY 4.0 attribution applies
- Statistics context: KOSIS/KOSTAT public statistics, MOIS resident-registration population statistics
- Full notices: [LICENSE](../LICENSE), [NOTICE](legal/NOTICE.md), [THIRD_PARTY_NOTICES](legal/THIRD_PARTY_NOTICES.md)
- Citation format: [CITATION.cff](../CITATION.cff)
- Methodology: [docs/legal/METHODOLOGY_AND_RIGHTS.md](legal/METHODOLOGY_AND_RIGHTS.md)

Closed-source commercial use, internal SaaS, redistributed products, or use cases that cannot adopt AGPL terms may require a separate written commercial license or dual-license arrangement.

Contact: woooya129 [at] gmail [dot] com

US twin project: [us-fashion-persona](https://github.com/woooya129-ai/us-fashion-persona)
