---
name: public-data-integration
description: Use when adding or evaluating Korean government statistics, KOSIS/KOSTAT data, public APIs, licenses, units, and costs.
---

# Public Data Integration

## Source Order

1. Official API/documentation.
2. Official dataset download or table metadata.
3. Official GitHub or Hugging Face source.
4. Academic source with peer-review status stated.

## Evaluation Criteria

- Free or paid.
- Authentication and quota.
- License and redistribution.
- Update cadence.
- Geographic and demographic granularity.
- Unit type: KRW, index, percent, count, score, text.
- Missing value behavior.
- Testability without live network.

## Implementation Rules

- Store source, period, unit, and label together.
- Do not convert non-KRW indicators to KRW.
- Add deterministic fallback fixtures for tests.
- Make external data optional so the app still runs without API credentials.
- State that public statistics are aggregate context, not individual inference.
