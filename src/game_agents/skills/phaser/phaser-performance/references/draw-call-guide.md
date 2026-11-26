# Phaser 3 WebGL Draw Call & Batching Guide

- **Why Draw Calls Matter**: Every texture switch or blend-mode change flushes the WebGL batch pipeline.
- **How to Batch**:
  1. Combine sprites into a single PNG + JSON Texture Atlas (TexturePacker / ShoeBox).
  2. Group `BitmapText` or `Image` objects with the same atlas consecutively in the display list.
  3. Set `roundPixels: true` in `Phaser.Game` config for crisp 2D pixel art without sub-pixel shimmering.
  4. Use `Phaser.Tilemaps` with baked tilesets rather than creating hundreds of individual `add.image()` tiles.
