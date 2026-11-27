---
name: game-architecture
description: Design clean, modular game architecture separating pure rules/state from engine rendering. Use when planning a new game, refactoring monolithic scenes, or designing multi-scene state flow.
---

# Game Architecture Skill

## Goal
Keep game rules, physics, and state decoupled from rendering so games remain testable, maintainable, and frame-rate independent.

## When to use
- Planning a new game project or major feature
- Refactoring a large scene file where rules and rendering are mixed
- Designing state sharing across multiple scenes (Boot, Game, UI)

## Workflow
1. Place pure game rules and data models in `src/engine/` or `src/systems/`.
2. Place scene lifecycle, sprites, input, and HUD in `src/scenes/` or `src/ui/`.
3. Connect gameplay scenes to UI scenes via typed events or a shared state store.
4. Use delta time (`delta`) for all movement, timers, and animations.

## Rules
- Never couple pure rule validation (chess legality, combat math, inventory) to DOM or canvas objects.
- Always clean up global event listeners and timers on scene shutdown.

## Reference
For multi-scene state patterns, read `references/state-management.md`.
