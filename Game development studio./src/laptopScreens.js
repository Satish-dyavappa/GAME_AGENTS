/**
 * Real-time Terminal Canvas Renderer for each GAME_AGENTS employee's 3D laptop screen
 * and Inspector Modal. Displays actual streamed tool calls, commands, and agent logs
 * with zero dummy/hardcoded work screens.
 */

const LEVEL_COLORS = {
  cmd: '#38bdf8',
  ok: '#4ade80',
  err: '#f87171',
  warn: '#fbbf24',
  info: '#cbd5e1',
};

function getStatusBadge(employee) {
  if (employee.needsInput) {
    return { label: 'NEEDS INPUT', bg: '#f59e0b', fg: '#0f172a' };
  }
  if (employee.working) {
    return { label: 'WORKING', bg: '#22c55e', fg: '#0f172a' };
  }
  return { label: 'IDLE', bg: '#334155', fg: '#e2e8f0' };
}

export function renderLaptopScreen(ctx, width, height, timeSec, employee) {
  ctx.save();

  // Terminal background
  ctx.fillStyle = '#070b14';
  ctx.fillRect(0, 0, width, height);

  // Header bar
  const badge = getStatusBadge(employee);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, width, 32);
  ctx.fillStyle = badge.bg;
  ctx.fillRect(0, 30, width, 2);

  // Window dots
  ['#ef4444', '#f59e0b', '#22c55e'].forEach((c, i) => {
    ctx.fillStyle = c;
    ctx.beginPath();
    ctx.arc(14 + i * 14, 16, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  // Agent title
  ctx.fillStyle = '#f8fafc';
  ctx.font = 'bold 12px ui-monospace, monospace';
  ctx.fillText(`${employee.name} — Live Terminal`, 62, 20);

  // Status pill on top right
  ctx.fillStyle = badge.bg;
  ctx.beginPath();
  ctx.roundRect(width - 106, 6, 94, 20, 4);
  ctx.fill();
  ctx.fillStyle = badge.fg;
  ctx.font = 'bold 10px ui-monospace, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(badge.label, width - 59, 19);
  ctx.textAlign = 'left';

  // Active task bar
  ctx.fillStyle = '#111827';
  ctx.fillRect(10, 38, width - 20, 24);
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px ui-monospace, monospace';
  const taskStr = employee.task || 'Idle — waiting for user prompt';
  const maxTaskChars = Math.floor((width - 36) / 6.8);
  const clippedTask = taskStr.length > maxTaskChars ? taskStr.slice(0, maxTaskChars - 3) + '...' : taskStr;
  ctx.fillText(`TASK: ${clippedTask}`, 18, 54);

  // Real streamed terminal lines
  const lines = Array.isArray(employee.terminalLines) && employee.terminalLines.length > 0
    ? employee.terminalLines
    : [{ text: `$ ${employee.name} ready. Send a prompt to begin.`, level: 'info' }];

  const startY = 82;
  const lineH = 18;
  const bottomMargin = 34;
  const maxVisibleLines = Math.max(4, Math.floor((height - startY - bottomMargin) / lineH));
  const visible = lines.slice(-maxVisibleLines);
  const maxChars = Math.floor((width - 32) / 6.8);

  ctx.font = '11.5px ui-monospace, monospace';
  visible.forEach((entry, idx) => {
    const rawText = typeof entry === 'string' ? entry : entry.text || '';
    const level = typeof entry === 'string' ? 'info' : entry.level || 'info';
    const text = rawText.length > maxChars ? rawText.slice(0, maxChars - 3) + '...' : rawText;

    ctx.fillStyle = LEVEL_COLORS[level] || LEVEL_COLORS.info;
    ctx.fillText(text, 16, startY + idx * lineH);
  });

  // Blinking cursor on active terminal
  if (employee.working || Math.floor(timeSec * 2) % 2 === 0) {
    const cursorY = startY + visible.length * lineH - 10;
    if (cursorY < height - bottomMargin) {
      ctx.fillStyle = employee.working ? '#4ade80' : '#475569';
      ctx.fillRect(16, cursorY, 8, 12);
    }
  }

  // Bottom status / approval overlay
  if (employee.needsInput) {
    const blink = Math.floor(timeSec * 2.5) % 2 === 0;
    ctx.fillStyle = blink ? 'rgba(245, 158, 11, 0.95)' : 'rgba(180, 83, 9, 0.95)';
    ctx.fillRect(10, height - 28, width - 20, 20);
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 11px ui-monospace, monospace';
    ctx.fillText('! WAITING FOR YOUR INPUT — PRESS [E] TO RESPOND', 18, height - 14);
  } else if (employee.working) {
    ctx.fillStyle = 'rgba(22, 163, 74, 0.2)';
    ctx.fillRect(10, height - 28, width - 20, 20);
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 1;
    ctx.strokeRect(10, height - 28, width - 20, 20);
    ctx.fillStyle = '#4ade80';
    ctx.font = 'bold 11px ui-monospace, monospace';
    ctx.fillText('● LIVE AGENT EXECUTION IN PROGRESS...', 18, height - 14);
  }

  ctx.restore();
}
