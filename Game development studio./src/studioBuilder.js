import * as THREE from 'three';
import { TEAMS } from './data/studioData.js';

function createSignTexture(title, subtitle, accentColor, width = 1024, height = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#0b1120';
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = accentColor;
  ctx.lineWidth = 8;
  ctx.strokeRect(8, 8, width - 16, height - 16);

  ctx.fillStyle = accentColor;
  ctx.font = 'bold 54px Inter, system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(title, width / 2, height * 0.46);

  ctx.fillStyle = '#e2e8f0';
  ctx.font = '600 32px Inter, system-ui, sans-serif';
  ctx.fillText(subtitle, width / 2, height * 0.78);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function buildStudio(scene) {
  const colliders = [];
  const addCollider = (cx, cz, halfW, halfD) => {
    colliders.push({
      minX: cx - halfW,
      maxX: cx + halfW,
      minZ: cz - halfD,
      maxZ: cz + halfD,
    });
  };

  // Lighting
  const hemi = new THREE.HemisphereLight(0xdbeafe, 0x1e293b, 0.95);
  scene.add(hemi);

  const dirLight = new THREE.DirectionalLight(0xfff7ed, 1.15);
  dirLight.position.set(10, 18, 12);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(2048, 2048);
  dirLight.shadow.camera.near = 1;
  dirLight.shadow.camera.far = 55;
  dirLight.shadow.camera.left = -24;
  dirLight.shadow.camera.right = 24;
  dirLight.shadow.camera.top = 20;
  dirLight.shadow.camera.bottom = -20;
  scene.add(dirLight);

  // Floor
  const floorGeo = new THREE.PlaneGeometry(44, 34);
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x1e2433,
    roughness: 0.78,
    metalness: 0.12,
  });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const grid = new THREE.GridHelper(44, 44, 0x334155, 0x263042);
  grid.position.y = 0.005;
  scene.add(grid);

  // Perimeter Walls
  const wallMat = new THREE.MeshStandardMaterial({ color: 0x151c2c, roughness: 0.85 });
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0x38bdf8,
    transparent: true,
    opacity: 0.18,
    roughness: 0.1,
    metalness: 0.1,
  });

  const wallHeight = 5.5;
  // North wall
  const northWall = new THREE.Mesh(new THREE.BoxGeometry(44, wallHeight, 0.4), wallMat);
  northWall.position.set(0, wallHeight / 2, -17);
  scene.add(northWall);

  // South wall
  const southWall = new THREE.Mesh(new THREE.BoxGeometry(44, wallHeight, 0.4), wallMat);
  southWall.position.set(0, wallHeight / 2, 17);
  scene.add(southWall);

  // West & East walls with glass windows
  [-22, 22].forEach((wx) => {
    const lower = new THREE.Mesh(new THREE.BoxGeometry(0.4, 1.1, 34), wallMat);
    lower.position.set(wx, 0.55, 0);
    scene.add(lower);

    const upper = new THREE.Mesh(new THREE.BoxGeometry(0.4, 1.0, 34), wallMat);
    upper.position.set(wx, 5.0, 0);
    scene.add(upper);

    const glass = new THREE.Mesh(new THREE.BoxGeometry(0.12, 3.4, 34), glassMat);
    glass.position.set(wx, 2.8, 0);
    scene.add(glass);
  });

  // Ceiling beams
  const beamMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 });
  for (let z = -12; z <= 12; z += 6) {
    const beam = new THREE.Mesh(new THREE.BoxGeometry(43.6, 0.35, 0.45), beamMat);
    beam.position.set(0, 5.3, z);
    scene.add(beam);
  }

  // Main Studio Wall Sign (North Wall)
  const mainSignTex = createSignTexture(
    'GAME_AGENTS STUDIO',
    'LANGGRAPH MULTI-AGENT GAME DEVELOPMENT',
    '#38bdf8',
    1280,
    256
  );
  const mainSign = new THREE.Mesh(
    new THREE.PlaneGeometry(10.5, 2.1),
    new THREE.MeshBasicMaterial({ map: mainSignTex })
  );
  mainSign.position.set(0, 3.4, -16.75);
  scene.add(mainSign);

  // Team Pods: colored zone rugs, overhead banners, and point lights
  TEAMS.forEach((team) => {
    const { x, z } = team.zoneCenter;

    // Zone rug
    const rug = new THREE.Mesh(
      new THREE.PlaneGeometry(11.5, 7.6),
      new THREE.MeshStandardMaterial({
        color: 0x162032,
        roughness: 0.9,
      })
    );
    rug.rotation.x = -Math.PI / 2;
    rug.position.set(x, 0.012, z);
    rug.receiveShadow = true;
    scene.add(rug);

    // Glowing border strip around pod
    const borderMat = new THREE.MeshBasicMaterial({ color: team.color });
    const stripFront = new THREE.Mesh(new THREE.BoxGeometry(11.5, 0.02, 0.08), borderMat);
    stripFront.position.set(x, 0.02, z + 3.8);
    scene.add(stripFront);
    const stripBack = new THREE.Mesh(new THREE.BoxGeometry(11.5, 0.02, 0.08), borderMat);
    stripBack.position.set(x, 0.02, z - 3.8);
    scene.add(stripBack);

    // Overhead hanging team/project banner
    const signTex = createSignTexture(team.name.toUpperCase(), `Project: ${team.project}`, team.color);
    const bannerMat = new THREE.MeshBasicMaterial({ map: signTex, side: THREE.DoubleSide });
    const banner = new THREE.Mesh(new THREE.PlaneGeometry(5.8, 1.45), bannerMat);
    banner.position.set(x, 3.85, z - 1.6);
    scene.add(banner);

    // Subtle zone accent light
    const podLight = new THREE.PointLight(team.color, 2.8, 13, 1.5);
    podLight.position.set(x, 3.4, z);
    scene.add(podLight);
  });

  // Central Playtest & Coffee Lounge (at 0, 0)
  const loungeRug = new THREE.Mesh(
    new THREE.PlaneGeometry(5.6, 5.2),
    new THREE.MeshStandardMaterial({ color: 0x272038, roughness: 0.92 })
  );
  loungeRug.rotation.x = -Math.PI / 2;
  loungeRug.position.set(0, 0.015, 0);
  scene.add(loungeRug);

  // Lounge Sofa
  const sofaMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 });
  const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.45, 1.0), sofaMat);
  sofaBase.position.set(0, 0.225, 1.3);
  sofaBase.castShadow = true;
  scene.add(sofaBase);
  const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.65, 0.25), sofaMat);
  sofaBack.position.set(0, 0.65, 1.7);
  sofaBack.castShadow = true;
  scene.add(sofaBack);
  addCollider(0, 1.35, 1.7, 0.65);

  // Coffee Table
  const tableMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.5 });
  const coffeeTable = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.42, 0.9), tableMat);
  coffeeTable.position.set(0, 0.21, -0.1);
  coffeeTable.castShadow = true;
  scene.add(coffeeTable);
  addCollider(0, -0.1, 1.0, 0.55);

  // Big Playtest TV Screen on stand
  const tvStand = new THREE.Mesh(
    new THREE.BoxGeometry(2.6, 0.65, 0.5),
    new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 })
  );
  tvStand.position.set(0, 0.325, -1.9);
  scene.add(tvStand);
  addCollider(0, -1.9, 1.4, 0.35);

  const tvFrame = new THREE.Mesh(
    new THREE.BoxGeometry(2.7, 1.55, 0.1),
    new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.4 })
  );
  tvFrame.position.set(0, 1.5, -1.9);
  scene.add(tvFrame);

  const tvCanvas = document.createElement('canvas');
  tvCanvas.width = 1024;
  tvCanvas.height = 576;
  const tvCtx = tvCanvas.getContext('2d');
  const tvTex = new THREE.CanvasTexture(tvCanvas);
  tvTex.colorSpace = THREE.SRGBColorSpace;
  const tvScreen = new THREE.Mesh(
    new THREE.PlaneGeometry(2.5, 1.38),
    new THREE.MeshBasicMaterial({ map: tvTex })
  );
  tvScreen.position.set(0, 1.5, -1.84);
  scene.add(tvScreen);

  tvScreen.userData.isPlaytestTV = true;
  tvScreen.userData.tvButtons = [];
  tvScreen.userData.tvHeaderRegion = { uMin: 0, uMax: 1, vMin: 1 - 56 / 576, vMax: 1 };
  tvScreen.userData.tvGraphRegion = { uMin: 0, uMax: 1, vMin: 0, vMax: 1 - 276 / 576 };
  tvFrame.userData.isPlaytestTV = true;
  tvStand.userData.isPlaytestTV = true;

  // Decorative Potted Plants in corners & walkways
  const potMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.7 });
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.7 });
  const plantCoords = [
    [-19.5, -14.5],
    [19.5, -14.5],
    [-19.5, 14.5],
    [19.5, 14.5],
    [-3.4, -2.5],
    [3.4, 2.5],
  ];
  plantCoords.forEach(([px, pz]) => {
    const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.24, 0.55, 12), potMat);
    pot.position.set(px, 0.275, pz);
    pot.castShadow = true;
    scene.add(pot);

    const foliage = new THREE.Mesh(new THREE.DodecahedronGeometry(0.55, 0), leafMat);
    foliage.position.set(px, 0.95, pz);
    foliage.castShadow = true;
    scene.add(foliage);
    addCollider(px, pz, 0.45, 0.45);
  });

  // Update function for the central playtest TV (live employee buttons + token usage graph)
  const updateStudioAnimations = (timeSec, stations = []) => {
    const w = 1024;
    const h = 576;
    tvCtx.fillStyle = '#070b14';
    tvCtx.fillRect(0, 0, w, h);

    // Header bar
    tvCtx.fillStyle = '#0f172a';
    tvCtx.fillRect(0, 0, w, 56);
    tvCtx.fillStyle = '#38bdf8';
    tvCtx.fillRect(0, 54, w, 2);

    tvCtx.fillStyle = '#38bdf8';
    tvCtx.font = 'bold 22px Inter, system-ui, sans-serif';
    tvCtx.textAlign = 'left';
    tvCtx.fillText('PLAYTEST LOUNGE TV — AGENT COMMAND HUB', 24, 36);

    const activeCount = stations.filter((s) => !s.employee.needsInput).length;
    const waitCount = stations.length - activeCount;
    const totalTokens = stations.reduce((sum, s) => sum + (s.tokensUsed || 0), 0);

    tvCtx.fillStyle = '#e2e8f0';
    tvCtx.font = 'bold 16px ui-monospace, monospace';
    tvCtx.textAlign = 'right';
    tvCtx.fillText(
      `${activeCount} ACTIVE · ${waitCount} WAIT · ${(totalTokens / 1000).toFixed(1)}k TOKENS`,
      w - 24,
      35
    );

    // Employee List Buttons (4 columns x 2 rows for 7 GAME_AGENTS)
    const cols = 4;
    const padX = 24;
    const startY = 74;
    const gapX = 12;
    const gapY = 12;
    const btnW = (w - padX * 2 - gapX * (cols - 1)) / cols;
    const btnH = 82;
    const buttons = [];

    stations.forEach((st, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const bx = padX + col * (btnW + gapX);
      const by = startY + row * (btnH + gapY);

      // Button card
      tvCtx.fillStyle = st.employee.needsInput ? '#1c1917' : '#111827';
      tvCtx.strokeStyle = st.employee.needsInput ? '#f59e0b' : st.team.color;
      tvCtx.lineWidth = 2;
      tvCtx.beginPath();
      tvCtx.roundRect(bx, by, btnW, btnH, 8);
      tvCtx.fill();
      tvCtx.stroke();

      // Team color dot
      tvCtx.fillStyle = st.team.color;
      tvCtx.beginPath();
      tvCtx.arc(bx + 16, by + 22, 5.5, 0, Math.PI * 2);
      tvCtx.fill();

      // Employee Name
      tvCtx.fillStyle = '#f8fafc';
      tvCtx.font = 'bold 15px Inter, system-ui, sans-serif';
      tvCtx.textAlign = 'left';
      tvCtx.fillText(st.employee.name, bx + 28, by + 27);

      // Status Pill (ACTIVE / WAIT)
      const isWait = st.employee.needsInput;
      tvCtx.fillStyle = isWait ? '#f59e0b' : '#22c55e';
      tvCtx.beginPath();
      tvCtx.roundRect(bx + 12, by + 40, 62, 18, 9);
      tvCtx.fill();
      tvCtx.fillStyle = '#0f172a';
      tvCtx.font = 'bold 11px ui-monospace, monospace';
      tvCtx.textAlign = 'center';
      tvCtx.fillText(isWait ? 'WAIT' : 'ACTIVE', bx + 43, by + 53);

      // Token count on button
      tvCtx.fillStyle = '#94a3b8';
      tvCtx.font = 'bold 13px ui-monospace, monospace';
      tvCtx.textAlign = 'right';
      tvCtx.fillText(`${((st.tokensUsed || 0) / 1000).toFixed(1)}k tok`, bx + btnW - 12, by + 53);

      // Store UV bounds (note: Three.js UV v=1 is top, v=0 is bottom)
      buttons.push({
        stationIndex: i,
        uMin: bx / w,
        uMax: (bx + btnW) / w,
        vMin: 1 - (by + btnH) / h,
        vMax: 1 - by / h,
      });
    });
    tvScreen.userData.tvButtons = buttons;

    // Bottom Section: Live Token Usage Bar Graph
    const graphTop = 276;
    const graphH = 276;
    tvCtx.fillStyle = '#0b1120';
    tvCtx.strokeStyle = '#1e293b';
    tvCtx.lineWidth = 2;
    tvCtx.beginPath();
    tvCtx.roundRect(padX, graphTop, w - padX * 2, graphH, 10);
    tvCtx.fill();
    tvCtx.stroke();

    tvCtx.fillStyle = '#94a3b8';
    tvCtx.font = 'bold 13px ui-monospace, monospace';
    tvCtx.textAlign = 'left';
    tvCtx.fillText('TOKEN USAGE BY EMPLOYEE (CLICK ANY BUTTON OR PRESS [E])', padX + 16, graphTop + 24);

    if (stations.length > 0) {
      const maxTokens = Math.max(...stations.map((s) => s.tokensUsed || 0), 1000);
      const chartLeft = padX + 24;
      const chartW = w - (padX + 24) * 2;
      const barAreaTop = graphTop + 48;
      const barAreaH = graphH - 82;
      const slotW = chartW / stations.length;
      const barW = Math.min(44, slotW * 0.6);

      stations.forEach((st, i) => {
        const val = st.tokensUsed || 0;
        const bh = Math.max(8, (val / maxTokens) * barAreaH);
        const x = chartLeft + i * slotW + (slotW - barW) / 2;
        const y = barAreaTop + barAreaH - bh;

        tvCtx.save();
        tvCtx.globalAlpha = st.employee.needsInput ? 0.5 : 0.95;
        tvCtx.fillStyle = st.team.color;
        tvCtx.beginPath();
        tvCtx.roundRect(x, y, barW, bh, [4, 4, 0, 0]);
        tvCtx.fill();
        tvCtx.restore();

        tvCtx.fillStyle = '#e2e8f0';
        tvCtx.font = 'bold 12px ui-monospace, monospace';
        tvCtx.textAlign = 'center';
        tvCtx.fillText(`${(val / 1000).toFixed(1)}k`, x + barW / 2, y - 6);

        tvCtx.fillStyle = st.employee.needsInput ? '#fbbf24' : '#cbd5e1';
        tvCtx.font = 'bold 12px Inter, system-ui, sans-serif';
        tvCtx.fillText(st.employee.name.split(' ')[0], x + barW / 2, graphTop + graphH - 12);
      });
    }

    tvTex.needsUpdate = true;
  };

  return {
    colliders,
    addCollider,
    updateStudioAnimations,
    tvWorldPos: new THREE.Vector3(0, 1.2, -1.9),
    tvInteractables: [tvScreen, tvFrame, tvStand],
  };
}
