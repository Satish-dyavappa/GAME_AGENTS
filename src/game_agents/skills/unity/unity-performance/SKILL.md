---
name: unity-performance
description: Unity C# performance optimization, component caching, physics loop hygiene, and GC avoidance.
---

# Unity Performance Skill

1. **Cache Component References**:
   - Call `GetComponent<T>()` in `Awake()` and store in private fields—never inside `Update()`.
2. **Use `FixedUpdate()` for Physics**:
   - Apply `Rigidbody` / `Rigidbody2D` forces and velocities in `FixedUpdate()`, while reading input in `Update()`.
3. **Avoid String & LINQ Allocations in `Update()`**:
   - Cache `WaitForSeconds`, use `StringBuilder` for HUD text, and avoid LINQ queries in per-frame loops.
4. **Reference Docs**:
   - See `references/gc-allocation-guide.md` for zero-GC C# patterns.
