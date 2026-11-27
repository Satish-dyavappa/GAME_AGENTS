---
name: phaser-vite-ts
description: Scaffold, configure, and build complete Vite + TypeScript + Phaser 3 games. Use when creating a new Phaser TypeScript project or fixing missing scenes and Vite/TS build errors.
---

# Phaser Vite + TypeScript Skill

## Goal
Ensure every Vite + TypeScript + Phaser 3 project compiles cleanly with zero TypeScript errors and boots a playable scene in the browser.

## When to use
- Creating a new Phaser 3 game with `package.json` + Vite + TypeScript
- Fixing `Cannot find module './scenes/...'` or `import.meta.env` TypeScript errors

## Workflow
1. Write `package.json` (`phaser`, `vite`, `typescript`, `"build": "tsc --noEmit && vite build"`).
2. Write `tsconfig.json` and `src/vite-env.d.ts` (`/// <reference types="vite/client" />`).
3. Create `index.html` pointing `<script type="module" src="/src/main.ts"></script>`.
4. Create every scene imported in `src/main.ts` (`BootScene.ts`, `GameScene.ts`, `UIScene.ts`).
5. Run `npm install && npm run build` via `execute_command` to verify 0 errors.

## Rules
- Never import a scene in `main.ts` without creating its `.ts` file in `src/scenes/`.
- Skip optional linting/formatting files (`.eslintrc`, `.prettierrc`) unless explicitly requested.
- Never run blocking dev servers (`npm run dev`, `vite`) in verification commands; use `npm run build`.
