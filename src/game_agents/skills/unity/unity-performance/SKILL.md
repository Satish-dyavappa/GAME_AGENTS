---
name: unity-performance
description: Diagnose and fix FPS drops, GC spikes, and physics jitter in Unity C# projects. Use when profiling Unity frame time, MonoBehaviour Update() loops, or missing .meta files.
---

# Unity Performance Skill

## Goal
Eliminate per-frame GC allocations and heavy `Update()` bottlenecks without changing gameplay behavior.

## When to use
- Frame rate stutters caused by Garbage Collection spikes
- Heavy `GetComponent` or LINQ calls inside `Update()`
- Physics jitter or missing `.meta` references

## Workflow
1. Inspect MonoBehaviour scripts for `GetComponent`, `FindObjectOfType`, or string/LINQ allocations inside `Update()`.
2. Cache component references in `Awake()`.
3. Move `Rigidbody` / `Rigidbody2D` velocity and force logic into `FixedUpdate()`.
4. Run `unity_check_meta_files` to verify all `Assets/` have valid `.meta` files.

## Rules
- Never call `GameObject.Find` or `GetComponent<T>()` inside `Update()` or `FixedUpdate()`.
- Prefer `ObjectPool<T>` and `NonAlloc` physics APIs for projectiles and VFX.

## Reference
For zero-allocation C# patterns, read `references/gc-allocation-guide.md`.
