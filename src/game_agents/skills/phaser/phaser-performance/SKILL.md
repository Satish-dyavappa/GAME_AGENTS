---
name: phaser-performance
description: Optimize Phaser 3 rendering performance, draw calls, texture atlases, and sprite pooling.
---

# Phaser 3 Performance Skill

Use these techniques to keep Phaser 3 games running at a locked 60 FPS:

1. **Minimize Draw Calls**:
   - Pack UI icons, tiles, and character frames into a single **Texture Atlas** (`this.load.atlas(...)`) so Phaser batches them into one WebGL draw call.
   - Avoid mixing `Phaser.GameObjects.Text` excessively between sprites (each dynamic `Text` breaks batching; prefer `BitmapText` for HUD counters).
2. **Object Pooling**:
   - Use `this.add.group({ classType: Bullet, maxSize: 100, runChildUpdate: true })` with `get()` and `setActive(false).setVisible(false)` instead of `new` + `destroy()`.
3. **Avoid Per-Frame Allocations**:
   - Never call `this.add.*` or `new Phaser.Math.Vector2()` inside `update(time, delta)`.
4. **References & Helpers**:
   - Deep-dive batching rules: `references/draw-call-guide.md`
   - Audit sprite creation in a project: `python scripts/count_sprites.py <project_dir>`
