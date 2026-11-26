export const TEAMS = [
  {
    id: 'orchestration',
    name: 'Orchestration',
    project: 'FeatureDevelopmentWorkflow',
    genre: 'LangGraph Supervisor & Planner',
    color: '#38bdf8',
    zoneCenter: { x: -11, z: -6.5 },
    spawnPoint: { x: -4.8, z: -6.5, yaw: Math.PI / 2 },
  },
  {
    id: 'analysis',
    name: 'Analysis & Engines',
    project: 'ProjectAnalyzer & Adapters',
    genre: 'Phaser · Unity · Unreal · Three.js',
    color: '#a855f7',
    zoneCenter: { x: 11, z: -6.5 },
    spawnPoint: { x: 4.8, z: -6.5, yaw: -Math.PI / 2 },
  },
  {
    id: 'development',
    name: 'Development & Debug',
    project: 'Code · Review · Debug Loop',
    genre: 'Autonomous Tool-Calling Agents',
    color: '#4ade80',
    zoneCenter: { x: -11, z: 6.5 },
    spawnPoint: { x: -4.8, z: 6.5, yaw: Math.PI / 2 },
  },
  {
    id: 'testing',
    name: 'Testing & QA',
    project: 'QA & Playwright Verification',
    genre: 'Automated Regression & Playtest',
    color: '#fbbf24',
    zoneCenter: { x: 11, z: 6.5 },
    spawnPoint: { x: 4.8, z: 6.5, yaw: -Math.PI / 2 },
  },
];

export const EMPLOYEES = [
  // Pod 1: Orchestration (SupervisorAgent, PlannerAgent)
  {
    id: 'supervisor',
    name: 'SupervisorAgent',
    role: 'Orchestration Lead',
    teamId: 'orchestration',
    task: 'Evaluating user request & setting quality criteria for workflow run',
    screenType: 'supervisor',
    needsInput: false,
    agentPrompt:
      'SupervisorAgent online. Ready to kick off FeatureDevelopmentWorkflow or BugFixWorkflow — what feature should the studio build next?',
    quickReplies: ['Run FeatureDevelopmentWorkflow', 'Run BugFixWorkflow', 'Check studio status'],
    deskPos: { x: -13.0, z: -8.5 },
    deskRotY: 0,
    avatar: { shirt: '#0284c7', skin: '#f1c27d', hair: '#1e293b', glasses: true, headphones: false },
  },
  {
    id: 'planner',
    name: 'PlannerAgent',
    role: 'Execution & Approval Gate',
    teamId: 'orchestration',
    task: 'Idle — waiting for user prompt',
    screenType: 'planner',
    needsInput: false,
    working: false,
    agentPrompt:
      'Approval Gate reached in FeatureDevelopmentWorkflow: Plan covers 4 files across Three.js scene & player controller. Approve to dispatch DeveloperAgent?',
    quickReplies: ['Approve plan & start Developer', 'Revise plan for performance', 'Hold for review'],
    deskPos: { x: -9.0, z: -8.5 },
    deskRotY: 0,
    avatar: { shirt: '#0369a1', skin: '#ffdbac', hair: '#7c2d12', glasses: false, headphones: true },
  },

  // Pod 2: Analysis & Engines (ProjectAnalyzerAgent)
  {
    id: 'project_analyzer',
    name: 'ProjectAnalyzerAgent',
    role: 'Engine & Manifest Resolver',
    teamId: 'analysis',
    task: 'Idle — waiting for user prompt',
    screenType: 'analyzer',
    needsInput: false,
    working: false,
    agentPrompt:
      'Detected multiple engine targets in workspace. Which engine adapter should I bind for this run: ThreejsAdapter, PhaserAdapter, UnityAdapter, or UnrealAdapter?',
    quickReplies: ['Bind ThreejsAdapter', 'Bind PhaserAdapter', 'Bind UnityAdapter'],
    deskPos: { x: 11.0, z: -8.5 },
    deskRotY: 0,
    avatar: { shirt: '#9333ea', skin: '#c68642', hair: '#0f172a', glasses: true, headphones: false },
  },

  // Pod 3: Development & Debug (DeveloperAgent, CodeReviewerAgent, DebuggerAgent)
  {
    id: 'developer',
    name: 'DeveloperAgent',
    role: 'Universal Implementer',
    teamId: 'development',
    task: 'Executing file read/write tools & implementing planned feature modules',
    screenType: 'developer',
    needsInput: false,
    agentPrompt:
      'DeveloperAgent ready. I have tool-registry access to read, write, and patch project files. Any coding constraints I should follow?',
    quickReplies: ['Keep changes modular', 'Prioritize 60 FPS', 'Add inline docstrings'],
    deskPos: { x: -14.2, z: 4.5 },
    deskRotY: 0,
    avatar: { shirt: '#16a34a', skin: '#ffdbac', hair: '#92400e', glasses: true, headphones: true },
  },
  {
    id: 'code_reviewer',
    name: 'CodeReviewerAgent',
    role: 'Static & Architecture Review',
    teamId: 'development',
    task: 'Auditing DeveloperAgent diff for edge cases, coupling & engine rules',
    screenType: 'reviewer',
    needsInput: false,
    agentPrompt:
      'Code review pass in progress. Should I enforce strict type-checking and fail the gate on any lint warnings?',
    quickReplies: ['Strict review gate', 'Warn only & continue'],
    deskPos: { x: -11.0, z: 4.5 },
    deskRotY: 0,
    avatar: { shirt: '#15803d', skin: '#e0ac69', hair: '#27272a', glasses: false, headphones: false },
  },
  {
    id: 'debugger',
    name: 'DebuggerAgent',
    role: 'Retry Loop & Root-Cause Fixer',
    teamId: 'development',
    task: 'Standing by on QA retry loop to diagnose runtime & test failures',
    screenType: 'debugger',
    needsInput: false,
    agentPrompt:
      'DebuggerAgent standing by (max_debug_attempts=3). Send me any stack trace or failing test to diagnose.',
    quickReplies: ['Check last QA logs', 'Reset debug attempts'],
    deskPos: { x: -7.8, z: 4.5 },
    deskRotY: 0,
    avatar: { shirt: '#22c55e', skin: '#f1c27d', hair: '#1e293b', glasses: true, headphones: true },
  },

  // Pod 4: Testing & QA (QAAgent)
  {
    id: 'qa_agent',
    name: 'QAAgent',
    role: 'Automated QA & Playtest',
    teamId: 'testing',
    task: 'Idle — waiting for user prompt',
    screenType: 'qa',
    needsInput: false,
    working: false,
    agentPrompt:
      'QAAgent finished smoke suite. Should I run full Playwright headless verification on the build or fast unit checks only?',
    quickReplies: ['Run full Playwright QA', 'Fast unit checks only', 'Report & ship'],
    deskPos: { x: 11.0, z: 4.5 },
    deskRotY: 0,
    avatar: { shirt: '#d97706', skin: '#8d5524', hair: '#09090b', glasses: false, headphones: true },
  },
];

export function getTeamById(teamId) {
  return TEAMS.find((t) => t.id === teamId) || TEAMS[0];
}
