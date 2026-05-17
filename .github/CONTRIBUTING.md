# Contributing

By submitting a pull request, patch, issue attachment, or other contribution,
you agree that your contribution is licensed under the GNU Affero General Public
License v3.0 only, the same license used by this project.

SPDX-License-Identifier: AGPL-3.0-only

## Contribution Rights

Only submit material that you have the right to contribute. Do not submit code,
data, prompts, images, documentation, or generated output copied from a source
whose license is incompatible with AGPL-3.0-only or with this repository's
public release policy.

## Do Not Submit

Do not submit:

- API keys, tokens, passwords, private keys, or credentials
- `.env` files or local secret files
- private user data, private research data, or real customer material
- raw LLM responses from private runs
- bundled NVIDIA dataset rows or transformed dataset samples unless a maintainer
  explicitly requests them and `docs/legal/THIRD_PARTY_NOTICES.md` is updated
- non-public planning docs, private operational logs, release reviews, or local
  machine paths
- claims that the tool predicts real purchase rate, real sales outcome, market
  share, trend performance, or real consumer taste

## Project Scope

This project is a local-first synthetic persona pre-screening tool for K-fashion
product concepts. Contributions should preserve that scope.

The maintainer may decline changes that conflict with the project positioning,
licensing, branding policy, data boundary, or public-release safety rules.

## DCO Sign-Off

All contributions must include a Developer Certificate of Origin 1.1 sign-off
in each commit message:

```text
Signed-off-by: Your Name <your.email@example.com>
```

You can add it with:

```powershell
git commit -s
```

The DCO sign-off means you certify that you have the right to submit the
contribution under the project's license. It is not a copyright assignment.

## Local Checks

Run these checks before opening a pull request:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run bandit -r src -c pyproject.toml
uv run pip-audit
uv run pre-commit run --all-files
```

Tests must not call real LLM providers or Hugging Face endpoints unless an
explicit integration-test path is approved by the maintainer.

## Commercial Or Dual-License Review

This project may offer separate written commercial license or dual-license terms
from the copyright holder.

By contributing, you acknowledge the copyright holder may distribute versions
of the project under additional written license terms, including commercial
license terms. Contributions are accepted into this public repository under
AGPL-3.0-only unless a separate written contributor agreement says otherwise.

Large, strategic, or externally authored contributions may require a separate
license review or contributor agreement before merge, so future commercial or
dual-license options remain clear.

Do not submit code you cannot license under the project terms.

## Branding

Do not present a fork, demo, hosted service, or derivative as the official
project. See `docs/legal/BRANDING_POLICY.md`.

## Third-Party Notices

If a contribution adds or changes third-party material, update
`docs/legal/THIRD_PARTY_NOTICES.md` in the same pull request.
