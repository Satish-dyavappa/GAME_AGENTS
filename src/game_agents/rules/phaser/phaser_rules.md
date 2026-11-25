# Phaser 3 Rules & Best Practices

- Organize gameplay into explicit `Phaser.Scene` subclasses with `preload()`, `create()`, and `update(time, delta)`.
- Use `this.physics.add` for Arcade Physics bodies and set world bounds cleanly.
- Avoid creating new listeners or textures inside `update()`.
- Load all assets in `preload()` with clear keys and relative paths.
- Ensure `index.html` cleanly loads Phaser 3 and initializes `new Phaser.Game(config)`.
