---
name: phaser-performance
description: Diagnose and fix FPS drops, lag, and memory issues in Phaser + TypeScript games. Use when the user reports lag, low FPS, stuttering, high draw calls, or poor performance on low-end Android devices.
---

# Phaser Performance Skill

## Goal
Find the root cause of a performance problem and propose the smallest
fix that reaches the target FPS. Do not change gameplay behavior.

## When to use
- Player reports lag or low FPS
- A level has many enemies, particles, or lights
- Memory grows over time (possible leak)

## Workflow
1. Ask for the target: device, FPS goal (default: 60 FPS on low-end Android).
2. Measure first. Never guess. Check:
   - Draw calls (`game.renderer.drawCount` or Spector.js)
   - Active game objects count
   - Texture memory and atlas usage
3. Identify the top bottleneck from the checklist below.
4. Propose ONE fix, explain why, and estimate the gain.
5. Hand the fix to the Developer Agent. Do not edit code yourself.

## Bottleneck checklist (check in this order)
1. **Draw calls:** sprites not in a shared texture atlas
2. **Object count:** enemies/bullets created and destroyed every frame (use object pooling)
3. **Particles/lights:** too many emitters or per-sprite light effects
4. **Update loops:** heavy logic inside `update()` every frame
5. **Memory leaks:** listeners or timers not removed on scene shutdown

## Rules
- Never remove gameplay features to gain FPS without asking the Game Design Agent.
- Prefer pooling, batching, and atlases over rewriting systems.
- If you cannot measure, say so. Do not invent numbers.

## Output format
Return exactly this structure:

```json
{
  "problem": "short description",
  "evidence": "measured numbers",
  "root_cause": "one sentence",
  "fix": "what to change",
  "expected_gain": "e.g. 300 -> 40 draw calls",
  "risk": "low | medium | high"
}
```

## Reference
For atlas packing details, read `references/draw-call-guide.md`.
To count sprites and objects in code, run `scripts/count_sprites.py <project_dir>`.
