# Three.js GPU Memory Disposal Guide

- Removing a mesh from `scene.remove(mesh)` does **not** free GPU buffers.
- Traverse the object hierarchy on teardown:
  ```js
  object.traverse((child) => {
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      const mats = Array.isArray(child.material) ? child.material : [child.material];
      mats.forEach((m) => m.dispose());
    }
  });
  ```
