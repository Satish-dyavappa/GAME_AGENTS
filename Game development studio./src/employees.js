import * as THREE from 'three';
import { EMPLOYEES, getTeamById } from './data/studioData.js';
import { renderLaptopScreen } from './laptopScreens.js';

function createAlertSpriteTexture() {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 96;
  const ctx = c.getContext('2d');

  ctx.fillStyle = '#f59e0b';
  ctx.beginPath();
  ctx.roundRect(12, 12, 232, 72, 20);
  ctx.fill();

  ctx.strokeStyle = '#fef3c7';
  ctx.lineWidth = 4;
  ctx.stroke();

  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 30px Inter, system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('! NEEDS INPUT', 128, 58);

  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/**
 * Spawns all 12 employees at their desks with a working laptop in front of each one.
 * Returns interactive station descriptors for proximity inspection & animation.
 */
export function buildEmployeesAndLaptops(scene, addCollider) {
  const stations = [];
  const alertTex = createAlertSpriteTexture();

  const deskWoodMat = new THREE.MeshStandardMaterial({ color: 0x3f2e21, roughness: 0.55 });
  const legMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.6, roughness: 0.4 });
  const chairMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 });
  const laptopBodyMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.7, roughness: 0.3 });
  const laptopDarkMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 });

  EMPLOYEES.forEach((emp, index) => {
    const team = getTeamById(emp.teamId);
    const group = new THREE.Group();
    group.position.set(emp.deskPos.x, 0, emp.deskPos.z);
    group.rotation.y = emp.deskRotY;
    scene.add(group);

    // Desk
    const deskTop = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.06, 0.95), deskWoodMat);
    deskTop.position.set(0, 0.74, 0);
    deskTop.castShadow = true;
    deskTop.receiveShadow = true;
    group.add(deskTop);

    [
      [-0.95, -0.4],
      [0.95, -0.4],
      [-0.95, 0.4],
      [0.95, 0.4],
    ].forEach(([lx, lz]) => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.74, 0.06), legMat);
      leg.position.set(lx, 0.37, lz);
      leg.castShadow = true;
      group.add(leg);
    });

    // Coffee mug on desk
    const mug = new THREE.Mesh(
      new THREE.CylinderGeometry(0.045, 0.04, 0.1, 10),
      new THREE.MeshStandardMaterial({ color: team.color, roughness: 0.4 })
    );
    mug.position.set(0.65, 0.82, 0.12);
    group.add(mug);

    // Laptop in front of employee (screen faces +Z toward employee)
    const laptopGroup = new THREE.Group();
    laptopGroup.position.set(0, 0.77, -0.05);
    group.add(laptopGroup);

    // Laptop keyboard base
    const laptopBase = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.022, 0.34), laptopBodyMat);
    laptopBase.position.set(0, 0.011, 0.08);
    laptopBase.castShadow = true;
    laptopGroup.add(laptopBase);

    const keyboardArea = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.005, 0.18), laptopDarkMat);
    keyboardArea.position.set(0, 0.023, 0.04);
    laptopGroup.add(keyboardArea);

    // Laptop hinged lid
    const lidPivot = new THREE.Group();
    lidPivot.position.set(0, 0.02, -0.08);
    lidPivot.rotation.x = -0.24; // Tilted slightly back for comfortable viewing
    laptopGroup.add(lidPivot);

    const lidBack = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.34, 0.018), laptopBodyMat);
    lidBack.position.set(0, 0.17, 0);
    lidBack.castShadow = true;
    lidPivot.add(lidBack);

    // Live CanvasTexture on the laptop screen
    const screenCanvas = document.createElement('canvas');
    screenCanvas.width = 512;
    screenCanvas.height = 320;
    const screenCtx = screenCanvas.getContext('2d');
    renderLaptopScreen(screenCtx, 512, 320, index * 1.7, emp);

    const screenTex = new THREE.CanvasTexture(screenCanvas);
    screenTex.colorSpace = THREE.SRGBColorSpace;
    const screenMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.48, 0.3),
      new THREE.MeshBasicMaterial({ map: screenTex })
    );
    screenMesh.position.set(0, 0.17, 0.011);
    lidPivot.add(screenMesh);

    // Office Chair at z = +0.62
    const seat = new THREE.Mesh(new THREE.BoxGeometry(0.54, 0.07, 0.52), chairMat);
    seat.position.set(0, 0.46, 0.62);
    seat.castShadow = true;
    group.add(seat);

    const chairBack = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.56, 0.07), chairMat);
    chairBack.position.set(0, 0.76, 0.86);
    chairBack.castShadow = true;
    group.add(chairBack);

    const chairPost = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.44, 8), legMat);
    chairPost.position.set(0, 0.22, 0.62);
    group.add(chairPost);

    // Employee Character (seated at z = +0.58 facing -Z toward laptop)
    const empGroup = new THREE.Group();
    empGroup.position.set(0, 0.5, 0.58);
    group.add(empGroup);

    const shirtMat = new THREE.MeshStandardMaterial({ color: emp.avatar.shirt, roughness: 0.75 });
    const skinMat = new THREE.MeshStandardMaterial({ color: emp.avatar.skin, roughness: 0.7 });
    const hairMat = new THREE.MeshStandardMaterial({ color: emp.avatar.hair, roughness: 0.8 });

    // Torso
    const torso = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.5, 0.24), shirtMat);
    torso.position.set(0, 0.28, 0);
    torso.castShadow = true;
    empGroup.add(torso);

    // Head
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.28, 0.28), skinMat);
    head.position.set(0, 0.69, -0.02);
    head.castShadow = true;
    empGroup.add(head);

    // Hair
    const hair = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.1, 0.3), hairMat);
    hair.position.set(0, 0.85, -0.02);
    empGroup.add(hair);

    // Glasses or Headphones
    if (emp.avatar.glasses) {
      const glasses = new THREE.Mesh(
        new THREE.BoxGeometry(0.24, 0.05, 0.03),
        new THREE.MeshStandardMaterial({ color: 0x0f172a })
      );
      glasses.position.set(0, 0.71, -0.165);
      empGroup.add(glasses);
    }
    if (emp.avatar.headphones) {
      const band = new THREE.Mesh(
        new THREE.TorusGeometry(0.16, 0.02, 6, 12, Math.PI),
        new THREE.MeshStandardMaterial({ color: team.color })
      );
      band.rotation.y = Math.PI / 2;
      band.position.set(0, 0.75, -0.02);
      empGroup.add(band);
    }

    // Articulated Arms reaching toward laptop keyboard
    const leftArm = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.42), shirtMat);
    leftArm.position.set(-0.22, 0.34, -0.22);
    leftArm.rotation.x = 0.25;
    empGroup.add(leftArm);

    const rightArm = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.42), shirtMat);
    rightArm.position.set(0.22, 0.34, -0.22);
    rightArm.rotation.x = 0.25;
    empGroup.add(rightArm);

    // Floating AI Agent "Needs Input" beacon above the desk
    const alertSprite = new THREE.Sprite(
      new THREE.SpriteMaterial({ map: alertTex, transparent: true })
    );
    alertSprite.position.set(0, 2.05, 0.2);
    alertSprite.scale.set(1.15, 0.43, 1);
    alertSprite.visible = Boolean(emp.needsInput);
    group.add(alertSprite);

    // Tag interactive meshes for click raycasting
    screenMesh.userData.stationIndex = index;
    lidBack.userData.stationIndex = index;
    laptopBase.userData.stationIndex = index;
    torso.userData.stationIndex = index;
    head.userData.stationIndex = index;

    // Register desk collision box
    addCollider(emp.deskPos.x, emp.deskPos.z + 0.1, 1.15, 0.85);

    stations.push({
      employee: emp,
      team,
      worldPos: new THREE.Vector3(emp.deskPos.x, 1.0, emp.deskPos.z),
      screenCanvas,
      screenCtx,
      screenTex,
      leftArm,
      rightArm,
      head,
      alertSprite,
      interactables: [screenMesh, lidBack, laptopBase, torso, head],
      chatHistory: [
        {
          sender: emp.name,
          role: 'agent',
          text: emp.agentPrompt,
        },
      ],
      phaseOffset: index * 0.9,
    });
  });

  return stations;
}
