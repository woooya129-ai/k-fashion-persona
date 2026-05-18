---
name: regression-review
description: Use for code review, release readiness checks, and investigating CI or reviewer findings.
---

# Regression Review

Review findings first, ordered by severity.

## Hotspots

- `ruff format src tests --check` must pass.
- KOSIS/KOSTAT prompt context must preserve non-KRW units.
- Persona sampling must honor `sampling_seed` and report meaningful pre-sample counts.
- Agent Pack import must count bad files, missing JSON, prompt count mismatch, and missing persona IDs.
- Version metadata must stay aligned across package, lockfile, citation, docs, and HF metadata.
- Streamlit slider and direct number input state must synchronize after user changes.

## Review Output

- Findings with file and line when available.
- Open questions or assumptions.
- Test gaps and residual risk.
- Short change summary only after findings.

If there are no issues, say so directly and name remaining test gaps.
