# Subagent Orchestration

- `codex team` 명령어는 사용하지 않는다.
- subagent는 사용자가 명시적으로 요청한 경우에만 사용한다.
- 한 번에 열 수 있는 agent thread는 `.codex/config.toml`의 `agents.max_threads = 6`을 기준으로 한다.
- child agent nesting은 `agents.max_depth = 1` 기준으로 유지한다.
- main agent는 즉시 필요한 critical path 작업을 직접 수행하고, 병렬로 가능한 sidecar 작업만 위임한다.
- code edit subtask를 위임할 때는 파일 소유 범위를 명확히 나눈다.
- worker에게는 "다른 agent/사용자 변경을 되돌리지 말라"고 지시한다.
- explorer는 기본 읽기 전용이다.

## Recommended Role Split

- PM planning: `pm_planner`
- Code path mapping: `code_explorer`
- Python implementation: `backend_implementer`
- Streamlit/UI implementation: `frontend_streamlit`
- Public data/API verification: `data_api_researcher`
- Regression review: `qa_reviewer`
- Documentation/release sync: `docs_release_manager`
