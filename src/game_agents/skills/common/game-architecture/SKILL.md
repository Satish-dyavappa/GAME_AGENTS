---
name: game-architecture
description: Global game architecture principles including state separation, delta-time loops, and object pooling.
---

# Game Architecture Skill

Apply these core architectural patterns across all game engines:

1. **Separate Pure Rules/State from Rendering**:
   - Keep game rules (board logic, combat math, inventory, turn state) in pure, engine-independent modules (`src/engine/` or `src/systems/`).
   - Keep rendering, input listeners, and audio inside engine scene/view layers (`src/scenes/` or `src/ui/`).
2. **Frame-Rate Independent Loops**:
   - Multiply all movement, cooldowns, and animations by `delta` (seconds or normalized ms).
3. **Object Pooling**:
   - Reuse bullets, particles, enemies, and UI popups instead of allocating/destroying them every frame.
4. **Reference Docs**:
   - See `references/state-management.md` when designing multi-scene state transitions.
