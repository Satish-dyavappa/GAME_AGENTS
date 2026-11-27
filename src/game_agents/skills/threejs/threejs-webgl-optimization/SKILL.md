---
name: threejs-webgl-optimization
description: Diagnose and fix Three.js draw call bottlenecks, resize bugs, and WebGL GPU memory leaks. Use when optimizing 3D web scenes or disposing geometries, materials, and textures.
---

# Three.js WebGL Optimization Skill

## Goal
Keep 3D WebGL scenes smooth and leak-free by batching repeated meshes and disposing unused GPU resources.

## When to use
- High draw calls from many individual meshes
- GPU memory grows when switching scenes or recreating objects
- Blurry canvas or stretched aspect ratio on window resize

## Workflow
1. Inspect renderer, camera, and lighting setup with `threejs_inspect_canvas`.
2. Batch repeated static geometry using `THREE.InstancedMesh`.
3. Clamp pixel ratio (`Math.min(window.devicePixelRatio, 2)`) and update `camera.aspect` on resize.
4. Dispose unused geometries, materials, and textures on teardown.

## Rules
- Never assume `scene.remove(mesh)` frees GPU memory; always call `.dispose()`.
- Validate custom GLSL shaders with `threejs_validate_shaders` before shipping.

## Reference
For recursive GPU cleanup code, read `references/memory-disposal-guide.md`.
