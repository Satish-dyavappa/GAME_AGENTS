import * as THREE from 'three';

export class PlayerController {
  constructor(camera, domElement, colliders) {
    this.camera = camera;
    this.domElement = domElement;
    this.colliders = colliders;

    // Start at studio entrance looking toward the central lounge & north wall
    this.position = new THREE.Vector3(0, 1.65, 13.5);
    this.yaw = 0;
    this.pitch = -0.06;
    this.eyeHeight = 1.65;
    this.radius = 0.42;

    this.keys = new Set();
    this.isDragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;
    this.enabled = true;

    this.bindEvents();
    this.syncCamera();
  }

  bindEvents() {
    window.addEventListener('keydown', (e) => {
      if (document.activeElement && ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        return;
      }
      this.keys.add(e.code);
    });
    window.addEventListener('keyup', (e) => {
      this.keys.delete(e.code);
    });

    this.domElement.addEventListener('click', () => {
      if (!this.enabled) return;
      if (document.pointerLockElement !== this.domElement && this.domElement.requestPointerLock) {
        this.domElement.requestPointerLock();
      }
    });

    document.addEventListener('mousemove', (e) => {
      if (!this.enabled) return;
      if (document.pointerLockElement === this.domElement) {
        this.yaw -= e.movementX * 0.0022;
        this.pitch -= e.movementY * 0.0022;
        this.pitch = Math.max(-1.2, Math.min(1.1, this.pitch));
      } else if (this.isDragging) {
        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
        this.yaw -= dx * 0.004;
        this.pitch -= dy * 0.004;
        this.pitch = Math.max(-1.2, Math.min(1.1, this.pitch));
      }
    });

    this.domElement.addEventListener('mousedown', (e) => {
      if (!this.enabled) return;
      this.isDragging = true;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });
    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });
  }

  teleportTo(x, z, yaw = 0) {
    this.position.set(x, this.eyeHeight, z);
    this.yaw = yaw;
    this.pitch = -0.08;
    this.syncCamera();
  }

  canStandAt(x, z) {
    // Studio room bounds
    if (x < -21.2 || x > 21.2 || z < -16.2 || z > 16.2) return false;

    for (const box of this.colliders) {
      if (
        x + this.radius > box.minX &&
        x - this.radius < box.maxX &&
        z + this.radius > box.minZ &&
        z - this.radius < box.maxZ
      ) {
        return false;
      }
    }
    return true;
  }

  update(dt) {
    if (!this.enabled) return;

    const forward = new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw));
    const right = new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw));

    const move = new THREE.Vector3();
    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) move.add(forward);
    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) move.sub(forward);
    if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) move.add(right);
    if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) move.sub(right);

    if (move.lengthSq() > 0) {
      move.normalize();
      const speed = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight') ? 8.2 : 4.8;
      const step = move.multiplyScalar(speed * dt);

      // Axis-separated sliding collision
      const nextX = this.position.x + step.x;
      if (this.canStandAt(nextX, this.position.z)) {
        this.position.x = nextX;
      }
      const nextZ = this.position.z + step.z;
      if (this.canStandAt(this.position.x, nextZ)) {
        this.position.z = nextZ;
      }
    }

    this.syncCamera();
  }

  syncCamera() {
    this.camera.position.copy(this.position);
    const euler = new THREE.Euler(this.pitch, this.yaw, 0, 'YXZ');
    this.camera.quaternion.setFromEuler(euler);
  }
}
