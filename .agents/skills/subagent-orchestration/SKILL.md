---
name: subagent-orchestration
description: Use when the user explicitly asks to use subagents, parallel agents, or a team-style split for this project.
---

# Subagent Orchestration

Use this only when the user explicitly asks for subagents, parallel agents, or role-based agent work.

## Routing

- `pm_planner`: product scope, version scope, acceptance criteria.
- `code_explorer`: read-only code path and dependency map.
- `backend_implementer`: Python implementation in `src/` and tests.
- `frontend_streamlit`: Streamlit UI, README/HF presentation, state sync.
- `data_api_researcher`: official public data/API, unit, license, cost verification.
- `qa_reviewer`: regression, CI, security, release-risk review.
- `docs_release_manager`: docs, metadata, GitHub/HF release sync.

## Prompt Shape

When spawning agents, give each one:

- Role and exact objective.
- Read or write scope.
- Files or directories it owns.
- Files or directories it must not touch.
- Expected final output.
- Reminder that other agents and the user may have edits in the same worktree.

## Guardrails

- Do not spawn agents for generic "review deeply" or "analyze thoroughly" requests.
- Keep immediate critical path work in the main thread.
- Do not duplicate the same task across agents.
- Wait only when the next main-thread step depends on the result.
