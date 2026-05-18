---
name: planning-workflow
description: Use for update-PLAN.md, PM plans, version scope, roadmap decomposition, and agent-role work breakdowns.
---

# Planning Workflow

## Inputs

- Read `PLAN.md`, `update-PLAN.md`, README, and user-referenced files.
- If the user references `comment/`, treat it as local source material and do not commit it unless asked.

## Output

Write plans in PM terms:

- Objective.
- User-visible change.
- Non-goals.
- Workstreams.
- Acceptance criteria.
- Risks and mitigations.
- Suggested version scope.
- Suggested agent ownership.

## Version Heuristic

- Patch: bug fix, docs correction, no new user workflow.
- Minor 0.x.0: new user-visible workflow, new API/data source, new report section, image option, or significant UI control.
- Major is not expected while the project is still below 1.0.0.

## Quality Bar

- Tie every proposed feature to an actual user workflow.
- Keep free/public API dependencies behind clear fallback behavior.
- Do not imply real consumer research or revenue prediction.
