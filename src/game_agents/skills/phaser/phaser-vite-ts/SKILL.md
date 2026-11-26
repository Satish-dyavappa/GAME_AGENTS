---
name: phaser-vite-ts
description: Standard scaffold and build checklist for Vite + TypeScript + Phaser 3 games.
---

# Phaser 3 + Vite + TypeScript Skill

When creating a Vite + TypeScript Phaser 3 project, always create **all** required files before finishing:

1. **`package.json`**: Include `phaser`, `vite`, and `typescript` with `"build": "tsc --noEmit && vite build"`.
2. **`tsconfig.json`** & **`src/vite-env.d.ts`**: Include `/// <reference types="vite/client" />` so `import.meta.env` compiles cleanly.
3. **`index.html`**: Point `<script type="module" src="/src/main.ts"></script>`.
4. **All Imported Scenes (`src/scenes/`)**: Never import a scene in `src/main.ts` unless its `.ts` file exists (`BootScene.ts`, `GameScene.ts`, `UIScene.ts`).
5. **Verify Build**: Run `npm install && npm run build` via `execute_command` to confirm 0 TypeScript errors.
