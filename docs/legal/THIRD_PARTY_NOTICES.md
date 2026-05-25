# Third-Party Notices

This file lists third-party datasets, libraries, and materials referenced by
k-fashion-persona. It is an attribution and notice file, not a license
override.

## NVIDIA Nemotron-Personas-Korea

- Provider: NVIDIA Corporation
- Source: Hugging Face dataset card, `nvidia/Nemotron-Personas-Korea`
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Use in this project: documented dataset loading and synthetic persona-based
  evaluation workflow
- Dataset bundled in this repository: No
- Changes to dataset content included in this repository: None
- Endorsement: No endorsement by NVIDIA is implied

Attribution statement:

> NVIDIA Nemotron-Personas-Korea is provided by NVIDIA Corporation and licensed
> under CC BY 4.0. This project may reference the dataset for synthetic
> persona-based evaluation workflows. This project is not affiliated with or
> endorsed by NVIDIA.

If any dataset sample, transformed row, generated persona text, or derived
artifact is later added to the public repository, update this section with the
exact file path, transformation method, and change statement before release.

## KOSIS / KOSTAT Public Statistics

- Provider: KOSIS / KOSTAT public statistics. Current public-data portal
  metadata may list the KOSIS API provider as National Data Office.
- Use in this project: report and prompt context based on household clothing
  and footwear spending, household income, disposable income, assets, debt, and
  net assets
- Not used for: direct inference of individual persona income, assets, or real
  purchasing power
- Data bundled in this repository: Yes, as `data/public/kosis_household_context.csv`
- Source pages used in the committed snapshot:
  - 2025 Q4 household income and expenditure public briefing:
    https://www.korea.kr/briefing/policyBriefingView.do?newsId=156746265
  - 2025 household finance and welfare public briefing:
    https://www.korea.kr/news/policyNewsView.do?newsId=156733201

## MOIS Resident-Registration Population

- Provider: Ministry of the Interior and Safety (MOIS), via the resident
  registration population statistics page and data.go.kr OpenAPI.
- Use in this project: report-only aggregate population context for selected
  age-bucket, sex, and province filters.
- Not used for: score weighting, market sizing, individual demand inference,
  or individual purchasing-power inference.
- Data bundled in this repository: Yes, as `data/public/mois_population_context.csv`
- Snapshot period: 2026-04.
- Source pages used:
  - MOIS resident-registration population statistics:
    https://jumin.mois.go.kr/agePpltStus.do
  - data.go.kr OpenAPI `15108072`:
    https://www.data.go.kr/data/15108072/openapi.do
- Operational notes observed on the public-data portal: JSON/XML API, free use,
  development traffic limit shown as 10,000, and no explicit use restriction.
- Scope note: resident-registration population includes residents,
  registration-unknown residents, and overseas Koreans in the resident
  registration system; foreigners are excluded.
- Granularity note: the OpenAPI can expose lower administrative rows
  such as city/county/district and neighborhood rows. This project aggregates
  those rows to province level before reporting.

## SGIS S-Open API Spatial Statistics

- Provider: SGIS / KOSTAT.
- Source page: https://sgis.mods.go.kr/contents/shortcut/shortcut_06.jsp
- Official-source check: 2026-05-19. The SGIS page lists S-Open API guidance
  and API key application under the public SGIS service.
- Use in this project: optional report-only aggregate spatial context for
  selected province-level filters.
- Not used for: persona sampling changes, prompt cache-key changes, score
  weighting, or individual demand inference.
- Data bundled in this repository: No.
- Credential contract: `SGIS_CONSUMER_KEY`, `SGIS_CONSUMER_SECRET`, and an
  optional reviewed `SGIS_SPATIAL_API_URL`.

## SBDC Commercial-Area Information API

- Provider: 소상공인시장진흥공단, via data.go.kr.
- Source page: https://www.data.go.kr/data/15012005/openapi.do
- Official-source check: 2026-05-19. The data.go.kr page lists REST API,
  JSON/XML format, free use, and no explicit use restriction on the metadata
  visible at check time.
- Use in this project: optional report-only aggregate commercial-area industry
  counts/distribution for selected region and offline-context inputs.
- Not used for: direct inference of demand, sales, revenue, or individual
  purchasing behavior.
- Data bundled in this repository: No.
- Raw-field policy: store names, addresses, coordinates, and other raw
  business-location fields are not written into reports.
- Credential contract: `DATAGOKR_SERVICE_KEY` and an optional reviewed
  `SBDC_COMMERCIAL_API_URL`.

## KMA APIHub Weather Context

- Provider: Korea Meteorological Administration (KMA), via APIHub.
- Source page: https://apihub.kma.go.kr/apiList.do?seqApi=10
- Supplemental data.go.kr page: https://www.data.go.kr/data/15084084/openapi.do
- Official-source check: 2026-05-19. The APIHub page lists short-term forecast,
  ultra-short forecast/nowcast, grid coordinates, and `authKey` authentication
  examples.
- Use in this project: optional report-only weather/season context for
  weather-sensitive product inputs.
- Not used for: persona score adjustment, direct concept fitness decisions, or
  individual demand inference.
- Data bundled in this repository: No.
- Credential contract: `KMA_APIHUB_AUTH_KEY`, optional reviewed
  `KMA_WEATHER_API_URL`, and `KMA_FORECAST_NX`/`KMA_FORECAST_NY` grid values.

## KCA T-Price Consumer Goods Price Candidate

- Provider: Korea Consumer Agency (KCA), via T-Price / data.go.kr.
- Source pages:
  - data.go.kr OpenAPI `3043385`:
    https://www.data.go.kr/data/3043385/openapi.do
  - data.go.kr file/API `15083256`:
    https://www.data.go.kr/data/15083256/fileData.do
- Official-source check: 2026-05-19. The OpenAPI page lists REST/XML, free
  use, development traffic 2,000, real-time update, and attribution terms
  with possible third-party rights. The file/API page lists CSV source data
  with JSON/XML auto-conversion, monthly update, free use, and no explicit
  use restriction at check time.
- Use in this project: candidate only for future detailed report-only
  living-price context.
- Not used for: product price validation, apparel price comparison, persona
  scoring, sales or purchase inference, or prompt conditioning.
- Data bundled in this repository: No.
- Candidate policy: prefer the monthly `15083256` JSON/XML auto-conversion
  path if implemented. Treat the legacy REST/XML path as a backup candidate
  until HTTPS/auth behavior is verified.
- Raw-field policy: individual product names, store names, and raw item prices
  must not appear in the default report. Future detailed reports may show only
  aggregate living-price context with source, period, and unit.

## BOK ECOS Macro Context Candidate

- Provider: Bank of Korea (BOK), via ECOS Open API.
- Source pages:
  - ECOS Open API: https://ecos.bok.or.kr/api/
  - Official sample JSON:
    https://ecos.bok.or.kr/api/KeyStatisticList/sample/json/kr/1/10
  - BOK economic statistics work overview:
    https://www.bok.or.kr/portal/submain/submain/sts.do?menuNo=201659
- Official-source check: 2026-05-19. The official sample response exposes
  macro rows with `CLASS_NAME`, `KEYSTAT_NAME`, `DATA_VALUE`, `CYCLE`, and
  `UNIT_NAME`. Local verification of the sample endpoint on 2026-05-19 showed
  exchange-rate rows whose `UNIT_NAME` was `원`.
- Use in this project: candidate only for future detailed report-only macro
  context such as price level, rate, exchange-rate, and sentiment background.
- Not used for: persona scoring, demand prediction, sales prediction, or
  product-level price validation.
- Data bundled in this repository: No.
- Candidate policy: preserve ECOS `UNIT_NAME` and `CYCLE` exactly. Do not force
  KRW conversion. Publicly accessible official evidence for cost, quota, and
  raw-data redistribution terms was insufficient at check time, so raw ECOS
  snapshots must not be committed.

## Direct Python Dependencies

The public source repository lists dependencies in `pyproject.toml` and
`uv.lock`. These packages are not relicensed by this project.

| Package | Role | License metadata observed in local environment |
|---|---|---|
| `streamlit` | Local UI | Apache-2.0 |
| `pydantic` | Data validation | MIT |
| `pyyaml` | YAML parsing | MIT |
| `python-dotenv` | Environment loading helper | BSD-3-Clause |
| `httpx` | HTTP client | BSD-3-Clause |
| `pandas` | Dataframe processing | BSD-3-Clause |
| `datasets` | Hugging Face dataset loading | Apache-2.0 |
| `pyarrow` | Parquet support | Apache-2.0 |
| `pytest` | Tests | MIT |
| `respx` | HTTPX mocking in tests | BSD-3-Clause |
| `ruff` | Lint and format checks | MIT |
| `bandit` | Security lint | Apache-2.0 |
| `pip-audit` | Dependency vulnerability audit | Apache-2.0 |
| `pre-commit` | Local quality hooks | MIT |

Before publishing a binary distribution, container image, or hosted derivative,
run a fresh dependency license review and update this file if any dependency
requires additional notices.

## External Services

This project can be configured by the user to call third-party LLM providers or
Hugging Face from the user's own local environment. API keys and tokens are not
bundled with this repository. Each provider's own terms and pricing apply.
