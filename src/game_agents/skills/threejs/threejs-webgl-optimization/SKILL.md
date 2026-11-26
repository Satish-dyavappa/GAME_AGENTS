---
name: threejs-webgl-optimization
description: Three.js WebGL optimization, InstancedMesh batching, and GPU memory disposal.
---

# Three.js WebGL Optimization Skill

1. **Dispose GPU Resources**:
   - Always call `.dispose()` on unused `BufferGeometry`, `Material`, `Texture`, and `WebGLRenderTarget` instances.
   - See `references/memory-disposal-guide.md` for recursive scene cleanup.
2. **Batch Static Geometry**:
   - Use `THREE.InstancedMesh` for repeated props (trees, tiles, chairs, bullets) to render hundreds of objects in 1 draw call.
3. **Responsive Resize & Clamped DPR**:
   - Clamp `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` and update `camera.aspect` on `resize`.
