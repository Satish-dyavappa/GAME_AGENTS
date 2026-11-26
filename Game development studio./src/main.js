import * as THREE from 'three';
import { TEAMS } from './data/studioData.js';
import { buildStudio } from './studioBuilder.js';
import { buildEmployeesAndLaptops } from './employees.js';
import { PlayerController } from './playerController.js';
import { renderLaptopScreen } from './laptopScreens.js';

const canvas = document.getElementById('studio-canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0e17);
scene.fog = new THREE.Fog(0x0b0e17, 22, 52);

const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 100);

const { colliders, addCollider, updateStudioAnimations, tvWorldPos, tvInteractables } = buildStudio(scene);
const stations = buildEmployeesAndLaptops(scene, addCollider);
stations.forEach((st) => {
  st.tokensUsed = 0;
  st.tokenRate = 0;
  st.employee.working = false;
  st.employee.terminalLines = [
    { text: `$ ${st.employee.name} initialized. Ready for prompt.`, level: 'info' },
  ];
});
const player = new PlayerController(camera, canvas, colliders);

// Raycaster for clicking directly on any laptop, employee, or Playtest Lounge TV
const raycaster = new THREE.Raycaster();
const allInteractables = [...stations.flatMap((s) => s.interactables), ...tvInteractables];

// HUD Elements
const teamNav = document.getElementById('team-nav');
const activeCountEl = document.getElementById('active-count');
const pendingCountEl = document.getElementById('pending-count');
const openActiveListBtn = document.getElementById('open-active-list-btn');
const openTokenGraphBtn = document.getElementById('open-token-graph-btn');

const interactPrompt = document.getElementById('interact-prompt');
const promptName = document.getElementById('prompt-name');
const promptRole = document.getElementById('prompt-role');
const promptAlert = document.getElementById('prompt-alert');
const crosshair = document.getElementById('crosshair');

// Popup 1: Individual Employee Laptop & AI Agent Terminal
const laptopModal = document.getElementById('laptop-modal');
const modalTeamPill = document.getElementById('modal-team-pill');
const modalEmpName = document.getElementById('modal-emp-name');
const modalEmpRole = document.getElementById('modal-emp-role');
const modalAgentStatus = document.getElementById('modal-agent-status');
const modalTask = document.getElementById('modal-task');
const modalProject = document.getElementById('modal-project');
const inspectorCanvas = document.getElementById('inspector-canvas');
const inspectorCtx = inspectorCanvas.getContext('2d');
const chatLogEl = document.getElementById('agent-chat-log');
const quickRepliesEl = document.getElementById('quick-replies');
const agentInputForm = document.getElementById('agent-input-form');
const agentInput = document.getElementById('agent-input');

// Popup 2: Active & Waiting Employees List
const activeListModal = document.getElementById('active-list-modal');
const activeListSubtitle = document.getElementById('active-list-subtitle');
const activeFilterTabs = document.getElementById('active-filter-tabs');
const empDirectoryGrid = document.getElementById('emp-directory-grid');

// Popup 3: Token Usage Graph
const tokenGraphModal = document.getElementById('token-graph-modal');
const tvTotalTokensEl = document.getElementById('tv-total-tokens');
const tvTokenCanvas = document.getElementById('tv-token-canvas');
const tvTokenCtx = tvTokenCanvas.getContext('2d');

const teamButtons = new Map();
let nearestStation = null;
let nearPlaytestTV = false;
let inspectedStation = null;
let activeModalType = null; // 'laptop' | 'active-list' | 'token-graph' | null
let activeFilter = 'all';

function refreshHudAlerts() {
  const totalPending = stations.filter((s) => s.employee.needsInput).length;
  const totalActive = stations.length - totalPending;
  activeCountEl.textContent = String(totalActive);
  pendingCountEl.textContent = String(totalPending);

  TEAMS.forEach((team) => {
    const btn = teamButtons.get(team.id);
    if (!btn) return;
    const count = stations.filter((s) => s.team.id === team.id && s.employee.needsInput).length;
    const pill = btn.querySelector('.team-alert-pill');
    if (count > 0) {
      pill.textContent = `${count} !`;
      pill.style.display = 'inline-block';
    } else {
      pill.style.display = 'none';
    }
  });
}

// Populate Team Navigation Buttons
TEAMS.forEach((team, idx) => {
  const btn = document.createElement('button');
  btn.className = 'team-btn';
  btn.innerHTML = `
    <span class="team-dot" style="background:${team.color}"></span>
    <span>${idx + 1}. ${team.name}</span>
    <small>· ${team.project}</small>
    <span class="team-alert-pill" style="display:none"></span>
  `;
  btn.addEventListener('click', () => {
    player.teleportTo(team.spawnPoint.x, team.spawnPoint.z, team.spawnPoint.yaw);
  });
  teamNav.appendChild(btn);
  teamButtons.set(team.id, btn);
});
refreshHudAlerts();

function closeAllModals() {
  laptopModal.classList.add('hidden');
  activeListModal.classList.add('hidden');
  tokenGraphModal.classList.add('hidden');
  inspectedStation = null;
  activeModalType = null;
  player.enabled = true;
}

function lockPlayerForModal(type) {
  closeAllModals();
  activeModalType = type;
  player.enabled = false;
  if (document.pointerLockElement) {
    document.exitPointerLock();
  }
}

// --- POPUP 1: Individual Employee Laptop ---
function renderChatHistory(station) {
  chatLogEl.innerHTML = '';
  for (const msg of station.chatHistory) {
    const div = document.createElement('div');
    div.className = `chat-msg ${msg.role}`;
    const senderSpan = document.createElement('span');
    senderSpan.className = 'sender';
    senderSpan.textContent = msg.sender;
    div.appendChild(senderSpan);
    div.appendChild(document.createTextNode(msg.text));
    chatLogEl.appendChild(div);
  }
  chatLogEl.scrollTop = chatLogEl.scrollHeight;
}

function updateModalStatus(station) {
  if (station.employee.needsInput) {
    modalAgentStatus.textContent = '● WAITING FOR YOUR INPUT';
    modalAgentStatus.classList.add('needs-input');
  } else if (station.employee.working) {
    modalAgentStatus.textContent = '● AI AGENT WORKING';
    modalAgentStatus.classList.remove('needs-input');
  } else {
    modalAgentStatus.textContent = '● IDLE (READY)';
    modalAgentStatus.classList.remove('needs-input');
  }
  modalTask.textContent = station.employee.task;
}

function openLaptopModal(station) {
  lockPlayerForModal('laptop');
  inspectedStation = station;

  modalTeamPill.textContent = station.team.name;
  modalTeamPill.style.background = station.team.color;
  modalEmpName.textContent = station.employee.name;
  modalEmpRole.textContent = `${station.employee.role} · ${station.team.genre}`;
  modalProject.textContent = station.team.project;

  updateModalStatus(station);
  renderChatHistory(station);

  quickRepliesEl.innerHTML = '';
  (station.employee.quickReplies || []).forEach((chipText) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'quick-chip';
    chip.textContent = chipText;
    chip.addEventListener('click', () => submitAgentInput(chipText));
    quickRepliesEl.appendChild(chip);
  });

  laptopModal.classList.remove('hidden');
  setTimeout(() => agentInput.focus(), 50);
}

function generateAgentReply(station, userText) {
  const emp = station.employee;
  const lower = userText.toLowerCase();
  if (lower.includes('status') || lower.includes('progress')) {
    return `Current status on ${station.team.project}: "${emp.task}". Everything is compiling cleanly — ready for your next directive!`;
  }
  return `Got it, Director! Applying "${userText}" to ${station.team.project} right now. I've updated my ${emp.role.toLowerCase()} pipeline and pushed the change to my live workspace.`;
}

function submitAgentInput(text) {
  if (!inspectedStation) return;
  const trimmed = text.trim();
  if (!trimmed) return;

  const st = inspectedStation;
  st.chatHistory.push({
    sender: 'You (Studio Director)',
    role: 'user',
    text: trimmed,
  });

  st.employee.needsInput = false;
  st.employee.lastCommand = trimmed;
  st.employee.task = `Applying directive: "${trimmed}"`;
  st.tokensUsed += 1250;
  st.alertSprite.visible = false;

  st.chatHistory.push({
    sender: st.employee.name,
    role: 'agent',
    text: generateAgentReply(st, trimmed),
  });

  renderLaptopScreen(st.screenCtx, 512, 320, performance.now() / 1000 + st.phaseOffset, st.employee);
  st.screenTex.needsUpdate = true;

  renderChatHistory(st);
  updateModalStatus(st);
  refreshHudAlerts();
  agentInput.value = '';
}

agentInputForm.addEventListener('submit', (e) => {
  e.preventDefault();
  submitAgentInput(agentInput.value);
});

// --- POPUP 2: Active & Waiting Employees List ---
function renderActiveDirectory() {
  const activeCount = stations.filter((s) => !s.employee.needsInput).length;
  const waitCount = stations.length - activeCount;
  activeListSubtitle.textContent = `${activeCount} Active Working · ${waitCount} Waiting for Input`;

  const filtered = stations.filter((st) => {
    if (activeFilter === 'active') return !st.employee.needsInput;
    if (activeFilter === 'waiting') return st.employee.needsInput;
    return true;
  });

  empDirectoryGrid.innerHTML = '';
  filtered.forEach((st) => {
    const card = document.createElement('div');
    card.className = 'emp-dir-card';
    const badge = st.employee.needsInput
      ? '<span class="roster-alert">NEEDS INPUT</span>'
      : '<span class="roster-active">ACTIVE</span>';

    card.innerHTML = `
      <div class="emp-dir-top">
        <div style="display:flex;align-items:center;gap:8px">
          <span class="team-dot" style="background:${st.team.color};flex-shrink:0"></span>
          <div>
            <div class="emp-dir-name">${st.employee.name}</div>
            <div class="emp-dir-role">${st.employee.role} · ${st.team.project}</div>
          </div>
        </div>
        ${badge}
      </div>
      <div class="emp-dir-task">${st.employee.task}</div>
      <div class="emp-dir-bottom">
        <span class="emp-dir-tokens">${(st.tokensUsed / 1000).toFixed(1)}k tokens</span>
        <button type="button" class="emp-open-btn">Open Laptop</button>
      </div>
    `;
    card.querySelector('.emp-open-btn').addEventListener('click', () => openLaptopModal(st));
    empDirectoryGrid.appendChild(card);
  });
}

function openActiveListModal() {
  lockPlayerForModal('active-list');
  renderActiveDirectory();
  activeListModal.classList.remove('hidden');
}

activeFilterTabs.addEventListener('click', (e) => {
  const btn = e.target.closest('.filter-tab');
  if (!btn) return;
  activeFilter = btn.dataset.filter;
  activeFilterTabs.querySelectorAll('.filter-tab').forEach((t) => t.classList.toggle('active', t === btn));
  renderActiveDirectory();
});

// --- POPUP 3: Live Token Usage Graph ---
function renderTokenGraph() {
  if (activeModalType !== 'token-graph') return;
  const w = tvTokenCanvas.width;
  const h = tvTokenCanvas.height;
  const ctx = tvTokenCtx;
  ctx.clearRect(0, 0, w, h);

  const totalTokens = stations.reduce((sum, s) => sum + s.tokensUsed, 0);
  tvTotalTokensEl.textContent = `Total: ${(totalTokens / 1000).toFixed(1)}k tokens`;

  const maxTokens = Math.max(...stations.map((s) => s.tokensUsed), 1000);
  const padX = 24;
  const padTop = 34;
  const padBottom = 48;
  const chartH = h - padTop - padBottom;
  const slotW = (w - padX * 2) / stations.length;
  const barW = Math.min(48, slotW * 0.62);

  // Horizontal guide lines
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  [0.25, 0.5, 0.75, 1].forEach((f) => {
    const gy = padTop + chartH * (1 - f);
    ctx.beginPath();
    ctx.moveTo(padX, gy);
    ctx.lineTo(w - padX, gy);
    ctx.stroke();
  });

  stations.forEach((st, i) => {
    const x = padX + i * slotW + (slotW - barW) / 2;
    const barH = Math.max(8, (st.tokensUsed / maxTokens) * chartH);
    const y = padTop + chartH - barH;

    ctx.save();
    ctx.globalAlpha = st.employee.needsInput ? 0.55 : 1;
    ctx.fillStyle = st.team.color;
    ctx.beginPath();
    ctx.roundRect(x, y, barW, barH, [6, 6, 0, 0]);
    ctx.fill();
    ctx.restore();

    // Token value above bar
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 12px ui-monospace, monospace';
    ctx.textAlign = 'center';
    ctx.fillText(`${(st.tokensUsed / 1000).toFixed(1)}k`, x + barW / 2, y - 8);

    // Employee name & status below bar
    ctx.fillStyle = st.employee.needsInput ? '#fbbf24' : '#e2e8f0';
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.fillText(st.employee.name.split(' ')[0], x + barW / 2, h - 24);

    ctx.fillStyle = st.employee.needsInput ? '#f59e0b' : '#4ade80';
    ctx.font = 'bold 10px ui-monospace, monospace';
    ctx.fillText(st.employee.needsInput ? 'WAIT' : 'ACTIVE', x + barW / 2, h - 8);
  });
}

function openTokenGraphModal() {
  lockPlayerForModal('token-graph');
  tokenGraphModal.classList.remove('hidden');
  renderTokenGraph();
}

// HUD & Close button listeners
openActiveListBtn.addEventListener('click', openActiveListModal);
openTokenGraphBtn.addEventListener('click', openTokenGraphModal);
document.querySelectorAll('[data-close-modal]').forEach((el) => {
  el.addEventListener('click', closeAllModals);
});

// Click directly on a laptop, employee, or 3D Playtest TV region
let pointerDownPos = null;
canvas.addEventListener('mousedown', (e) => {
  pointerDownPos = { x: e.clientX, y: e.clientY };
});
canvas.addEventListener('mouseup', (e) => {
  if (!pointerDownPos || activeModalType) return;
  const moved = Math.hypot(e.clientX - pointerDownPos.x, e.clientY - pointerDownPos.y);
  if (moved > 5) return;

  const ndc = new THREE.Vector2();
  if (document.pointerLockElement === canvas) {
    ndc.set(0, 0);
  } else {
    ndc.set((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
  }

  raycaster.setFromCamera(ndc, camera);
  const hits = raycaster.intersectObjects(allInteractables, false);
  if (hits.length > 0 && hits[0].distance < 7.5) {
    const hit = hits[0];
    if (hit.object.userData.isPlaytestTV) {
      if (hit.uv) {
        const { x: u, y: v } = hit.uv;
        // 1. Clicked an employee button on the 3D TV -> open that employee's Laptop popup
        const matched = (hit.object.userData.tvButtons || []).find(
          (b) => u >= b.uMin && u <= b.uMax && v >= b.vMin && v <= b.vMax
        );
        if (matched && stations[matched.stationIndex]) {
          openLaptopModal(stations[matched.stationIndex]);
          return;
        }
        // 2. Clicked the Token Graph region on the 3D TV -> open Token Usage Graph popup
        const gr = hit.object.userData.tvGraphRegion;
        if (gr && u >= gr.uMin && u <= gr.uMax && v >= gr.vMin && v <= gr.vMax) {
          openTokenGraphModal();
          return;
        }
      }
      // 3. Clicked TV header/frame -> open Active Employees List popup
      openActiveListModal();
      return;
    }

    const idx = hit.object.userData.stationIndex;
    if (idx !== undefined && stations[idx]) {
      openLaptopModal(stations[idx]);
    }
  }
});

window.addEventListener('keydown', (e) => {
  const typingInInput = document.activeElement === agentInput;
  if (e.code === 'Escape' && activeModalType) {
    closeAllModals();
    return;
  }
  if (typingInInput) return;

  if (e.code === 'KeyE') {
    if (activeModalType) {
      closeAllModals();
    } else if (nearPlaytestTV) {
      openActiveListModal();
    } else if (nearestStation) {
      openLaptopModal(nearestStation);
    }
    return;
  }
  if (!activeModalType && ['Digit1', 'Digit2', 'Digit3', 'Digit4'].includes(e.code)) {
    const idx = Number(e.code.replace('Digit', '')) - 1;
    const team = TEAMS[idx];
    if (team) {
      player.teleportTo(team.spawnPoint.x, team.spawnPoint.z, team.spawnPoint.yaw);
    }
  }
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation Loop
let lastTime = performance.now();
let screenUpdateIdx = 0;
let screenTimer = 0;

function animate(now) {
  requestAnimationFrame(animate);
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  const timeSec = now / 1000;

  player.update(dt);

  let closest = null;
  let closestDist = 3.2;

  for (const st of stations) {
    const t = timeSec + st.phaseOffset;
    if (st.employee.working) {
      // Active typing animation only when the real agent is working
      st.leftArm.position.y = 0.34 + Math.sin(t * 14) * 0.015;
      st.rightArm.position.y = 0.34 + Math.cos(t * 15) * 0.015;
      st.head.rotation.y = Math.sin(t * 0.7) * 0.08;
      st.head.rotation.x = -0.12 + Math.sin(t * 1.3) * 0.03;
    } else {
      st.leftArm.position.y = 0.34;
      st.rightArm.position.y = 0.34;
      st.head.rotation.y = Math.sin(t * 0.25) * 0.03;
      st.head.rotation.x = -0.05;
    }

    if (st.alertSprite.visible) {
      st.alertSprite.position.y = 2.05 + Math.sin(timeSec * 3.5 + st.phaseOffset) * 0.08;
    }

    const d = player.position.distanceTo(st.worldPos);
    if (d < closestDist) {
      closestDist = d;
      closest = st;
    }
  }

  const tvDist = player.position.distanceTo(tvWorldPos);
  nearPlaytestTV = tvDist < 3.6 && tvDist <= closestDist;
  nearestStation = nearPlaytestTV ? null : closest;

  if (nearPlaytestTV && !activeModalType) {
    promptName.textContent = 'Playtest Lounge TV — Active Employees';
    promptRole.textContent = 'Press [E] for Active List, or Click any Employee / Graph on the TV';
    const anyPending = stations.some((s) => s.employee.needsInput);
    promptAlert.classList.toggle('hidden', !anyPending);
    interactPrompt.classList.remove('hidden');
    crosshair.classList.add('active');
  } else if (nearestStation && !activeModalType) {
    promptName.textContent = `${nearestStation.employee.name} — Open AI Laptop`;
    promptRole.textContent = `${nearestStation.employee.role} · ${nearestStation.team.project}`;
    promptAlert.classList.toggle('hidden', !nearestStation.employee.needsInput);
    interactPrompt.classList.remove('hidden');
    crosshair.classList.add('active');
  } else {
    interactPrompt.classList.add('hidden');
    crosshair.classList.remove('active');
  }

  screenTimer += dt;
  if (screenTimer > 0.08) {
    screenTimer = 0;
    for (let k = 0; k < 2; k++) {
      const st = stations[screenUpdateIdx % stations.length];
      renderLaptopScreen(st.screenCtx, 512, 320, timeSec + st.phaseOffset, st.employee);
      st.screenTex.needsUpdate = true;
      screenUpdateIdx++;
    }
    updateStudioAnimations(timeSec, stations);
  }

  if (activeModalType === 'laptop' && inspectedStation) {
    renderLaptopScreen(
      inspectorCtx,
      inspectorCanvas.width,
      inspectorCanvas.height,
      timeSec + inspectedStation.phaseOffset,
      inspectedStation.employee
    );
  } else if (activeModalType === 'token-graph') {
    renderTokenGraph();
  }

  renderer.render(scene, camera);
}

requestAnimationFrame(animate);
