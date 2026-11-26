# Unity Zero-GC Allocation Guide

- Use `CompareTag("Player")` instead of `gameObject.tag == "Player"` (avoids string allocation).
- Use `Physics.OverlapSphereNonAlloc` / `RaycastNonAlloc` with pre-allocated `Collider[]` buffers.
- Use `UnityEngine.Pool.ObjectPool<T>` for projectiles, VFX, and floating damage numbers.
