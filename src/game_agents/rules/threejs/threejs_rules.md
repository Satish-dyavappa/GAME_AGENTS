# Three.js Rules & Best Practices

- Dispose of unused `BufferGeometry`, `Material`, and `Texture` instances to avoid GPU memory leaks.
- Handle window `resize` events to update `camera.aspect` and `renderer.setSize()`.
- Use `requestAnimationFrame` with a `THREE.Clock` for smooth delta-timed animations.
