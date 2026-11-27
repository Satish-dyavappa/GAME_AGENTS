---
name: clean-code-testing
description: Enforce clean build verification, minimal diffs, and non-blocking QA test execution across all engines. Use during code review, debugging, and QA verification.
---

# Clean Code & Testing Skill

## Goal
Verify every code change with a real build or test run while avoiding wasted tool turns and hanging background processes.

## When to use
- Reviewing code changes before QA
- Running build or unit/integration tests in `QAAgent` or `DebuggerAgent`

## Workflow
1. Run one-shot build/typecheck (`npm run build`, `tsc --noEmit`, `dotnet build`).
2. Run unit tests (`npx vitest run`, `pytest`, `npm test`) if present.
3. For web games, verify runtime boot with `browser_console_logs` and `browser_screenshot`.

## Rules
- Never run blocking dev servers (`npm run dev`, `vite`) inside `execute_command`.
- Only run `git_diff` when the target game folder is a git repository.
- Report exact measured errors and file/line numbers; never invent passing results.
