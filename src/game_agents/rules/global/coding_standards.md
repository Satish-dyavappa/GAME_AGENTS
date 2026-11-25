# Global Game Development Coding Standards

- Always write modular, readable, and well-commented code.
- Use frame-rate independent delta time (`dt` / `delta`) for movement, physics, and animations.
- Never allocate large temporary objects inside hot `update()` / `tick()` loops.
- Clean up event listeners, timers, and textures when scenes or levels are destroyed.
- Keep game state separated from rendering logic where possible.
