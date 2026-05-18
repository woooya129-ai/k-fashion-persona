---
name: hf-space-release
description: Use when committing, pushing, tagging, or syncing GitHub main with the Hugging Face Space for this project.
---

# HF Space Release

## Preflight

- Check `git status --short`.
- Exclude `comment/`, `sandbox/`, `.local-notes/`, `claude-advisor/` unless the user explicitly asks.
- Confirm version metadata if release-related files changed.
- Run release gates before tagging or announcing release readiness.

## GitHub

- Stage only files in the intended scope.
- Commit with a short imperative message.
- Push `main` to `origin`.

## Hugging Face Space

- Sync after GitHub push when the user asks for HF Space update or when Space-visible files changed.
- Use the existing Hugging Face repo and keep Space metadata intact.
- Verify HF API and Space URL return success after upload.

## Final Report

Include:

- GitHub commit hash.
- Hugging Face commit hash when available.
- Checks run.
- Any intentionally untracked local files left behind.
