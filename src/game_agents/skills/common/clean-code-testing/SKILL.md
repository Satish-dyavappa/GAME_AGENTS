---
name: clean-code-testing
description: Global standards for clean modular code, build verification, and safe non-blocking QA testing.
---

# Clean Code & Verification Skill

1. **Always Verify Builds**:
   - After writing or editing code, run the project's build/typecheck command (`npm run build`, `tsc --noEmit`, `dotnet build`) before finishing.
2. **No Optional Tooling Bloat**:
   - Do not spend turns creating `.eslintrc` or `.prettierrc` unless explicitly requested; focus on runnable game code first.
3. **Non-Blocking QA Commands**:
   - Never run hanging dev servers (`npm run dev`, `vite`) inside `execute_command` without a timeout or backgrounding; use one-shot build/test commands (`npm run build`, `npx vitest run`).
