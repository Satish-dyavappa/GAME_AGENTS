---
name: unreal-cpp-patterns
description: Enforce Unreal Engine 5 C++ memory safety, reflection macros, and Tick optimization. Use when writing or reviewing Unreal C++ Actors, Components, or .uproject modules.
---

# Unreal Engine C++ Patterns Skill

## Goal
Write crash-free, GC-safe Unreal Engine C++ code that exposes cleanly to Blueprints and minimizes per-frame `Tick()` overhead.

## When to use
- Creating or reviewing `AActor`, `UActorComponent`, or `UObject` C++ classes
- Debugging dangling pointer crashes or Blueprint exposure issues

## Workflow
1. Inspect `.uproject` via `unreal_inspect_uproject` to confirm engine version and modules.
2. Verify all `UObject*` / `TObjectPtr<T>` member variables use `UPROPERTY()`.
3. Disable `PrimaryActorTick.bCanEverTick` unless per-frame updates are strictly required.

## Rules
- Follow Unreal prefixes strictly: `A` (Actor), `U` (UObject/Component), `F` (Struct), `E` (Enum), `I` (Interface).
- Prefer `FTimerHandle` and event delegates over polling in `Tick()`.
