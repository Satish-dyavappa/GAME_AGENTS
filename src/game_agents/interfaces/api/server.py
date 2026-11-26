"""Real-time FastAPI & WebSocket bridge connecting Python GAME_AGENTS to the Three.js 3D Office."""

import asyncio
import threading
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from game_agents.agents import (
    CodeReviewerAgent,
    DebuggerAgent,
    DeveloperAgent,
    PlannerAgent,
    ProjectAnalyzerAgent,
    QAAgent,
    SupervisorAgent,
)
from game_agents.core.contracts.task import Task, TaskPriority
from game_agents.workflows.feature_development import FeatureDevelopmentWorkflow


def _resolve_game_project_path(raw_path: str) -> Path:
    """Resolve the actual game project directory (e.g. ./workspace/chess inside ./workspace)."""
    p = Path(raw_path).resolve()
    if not p.exists():
        return p

    # If this folder already looks like a game project root, return it directly
    markers = ("package.json", "index.html", "Assets", "ProjectSettings", "project.godot")
    if any((p / m).exists() for m in markers) or list(p.glob("*.uproject")):
        return p

    # Otherwise, check immediate subdirectories (e.g., workspace/chess)
    subdirs = [d for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")]
    for d in subdirs:
        if any((d / m).exists() for m in markers) or list(d.glob("*.uproject")):
            return d

    if len(subdirs) == 1:
        return subdirs[0]
    return p
class ChatRequest(BaseModel):
    message: str = Field(..., description="Directive or question sent from the 3D laptop terminal")
    project_path: str = Field(default="./workspace", description="Target workspace path")
    engine: str | None = Field(default=None, description="Optional target engine override")


class WorkflowTriggerRequest(BaseModel):
    feature_description: str = Field(..., description="Feature prompt (e.g. 'Create a Phaser 3 chess game')")
    project_path: str = Field(default="./workspace", description="Target game workspace directory")
    require_approval: bool = Field(default=True, description="Pause at PlannerAgent for 3D Human Approval")
    max_debug_attempts: int = Field(default=2, description="Max Debugger -> Developer retry loops")


class ApprovalDecisionRequest(BaseModel):
    approved: bool = Field(..., description="True to proceed with DeveloperAgent, False to reject")


class StudioConnectionManager:
    """Manages active WebSocket clients (Three.js 3D Office instances)."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for conn in self.active_connections:
            try:
                await conn.send_json(event)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)


class StudioOrchestratorBridge:
    """Bridges live Python agents and LangGraph workflows with the 3D Studio UI."""

    def __init__(self) -> None:
        self.agents = {
            "supervisor": SupervisorAgent(),
            "planner": PlannerAgent(),
            "project_analyzer": ProjectAnalyzerAgent(),
            "developer": DeveloperAgent(),
            "code_reviewer": CodeReviewerAgent(),
            "debugger": DebuggerAgent(),
            "qa_agent": QAAgent(),
        }
        self.agent_states: dict[str, dict[str, Any]] = {
            agent_id: {
                "id": agent_id,
                "name": agent.config.name,
                "role": agent.config.role,
                "task": "Idle — waiting for user prompt",
                "needsInput": False,
                "working": False,
                "tokensUsed": 0,
                "terminalLines": [{"text": f"$ {agent.config.name} initialized. Ready for prompt.", "level": "info"}],
                "lastOutput": "",
            }
            for agent_id, agent in self.agents.items()
        }
        for agent_id, agent in self.agents.items():
            agent.on_event = self._make_event_handler(agent_id)

        self.ws_manager = StudioConnectionManager()
        self.loop: asyncio.AbstractEventLoop | None = None

        # Human approval gate synchronization
        self._approval_event = threading.Event()
        self._approval_decision = True
        self._pending_approval = False

    def _make_event_handler(self, agent_id: str):
        def _on_event(event_type: str, payload: dict[str, Any]) -> None:
            if event_type == "agent_start":
                self.update_agent_state(
                    agent_id,
                    task=f"Running: {payload.get('task', '')[:65]}",
                    needs_input=False,
                    working=True,
                )
                self.append_terminal_line(
                    agent_id,
                    f"$ [{payload.get('provider')}:{payload.get('model')}] {payload.get('task')}",
                    level="cmd",
                )
            elif event_type == "tool_call":
                args_str = ", ".join(f"{k}={repr(v)[:40]}" for k, v in (payload.get("args") or {}).items())
                self.append_terminal_line(agent_id, f"> {payload.get('tool')}({args_str})", level="cmd")
            elif event_type == "tool_result":
                ok = payload.get("success", True)
                out_preview = str(payload.get("output", "")).splitlines()[0][:80] if payload.get("output") else ""
                prefix = "OK" if ok else "ERR"
                self.append_terminal_line(
                    agent_id,
                    f"  [{prefix}] {out_preview}",
                    level="ok" if ok else "err",
                )
            elif event_type == "agent_finish":
                created = payload.get("files_created", [])
                modified = payload.get("files_modified", [])
                if created or modified:
                    self.append_terminal_line(
                        agent_id,
                        f"[DONE] created={len(created)} modified={len(modified)}",
                        level="ok",
                    )

        return _on_event

    def append_terminal_line(self, agent_id: str, line: str, level: str = "info") -> None:
        if agent_id not in self.agent_states:
            return
        st = self.agent_states[agent_id]
        lines = st.setdefault("terminalLines", [])
        lines.append({"text": line, "level": level})
        if len(lines) > 40:
            del lines[: len(lines) - 40]
        self._emit_sync({"type": "terminal_log", "agentId": agent_id, "line": {"text": line, "level": level}})

    def _emit_sync(self, event: dict[str, Any]) -> None:
        """Thread-safe broadcast from synchronous LangGraph / Agent worker threads."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.ws_manager.broadcast(event), self.loop)

    def update_agent_state(
        self,
        agent_id: str,
        *,
        task: str | None = None,
        needs_input: bool | None = None,
        working: bool | None = None,
        add_tokens: int = 0,
        chat_message: dict[str, str] | None = None,
    ) -> None:
        if agent_id not in self.agent_states:
            return
        st = self.agent_states[agent_id]
        if task is not None:
            st["task"] = task
        if needs_input is not None:
            st["needsInput"] = needs_input
        if working is not None:
            st["working"] = working
        if add_tokens:
            st["tokensUsed"] += add_tokens

        payload: dict[str, Any] = {"type": "agent_update", "agentId": agent_id, "state": dict(st)}
        if chat_message:
            payload["chatMessage"] = chat_message
        self._emit_sync(payload)

    def handle_agent_chat_sync(self, agent_id: str, req: ChatRequest) -> dict[str, Any]:
        agent = self.agents.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Unknown agent '{agent_id}'")

        # Check if user is answering a pending Planner approval gate
        if agent_id == "planner" and self._pending_approval:
            lower = req.message.lower()
            is_approved = any(w in lower for w in ["approve", "yes", "ok", "start", "proceed", "go"])
            self._approval_decision = is_approved
            self._pending_approval = False
            self._approval_event.set()
            reply = (
                "Plan approved! Dispatching DeveloperAgent to implement the feature now."
                if is_approved
                else "Plan rejected by Director. Halting workflow."
            )
            self.update_agent_state(
                "planner",
                task=reply,
                needs_input=False,
                working=False,
                add_tokens=320,
            )
            return {"agentId": agent_id, "success": True, "reply": reply, "state": self.agent_states[agent_id]}

        # Auto-workflow: SupervisorAgent automatically orchestrates the multi-agent pipeline for action directives
        lower_msg = req.message.lower()
        is_status_only = any(q in lower_msg for q in ["check studio status", "status only"])
        is_action = not is_status_only and any(
            kw in lower_msg
            for kw in [
                "workflow", "create", "build", "run", "fix", "debug", "make",
                "implement", "add", "update", "repair", "playable", "complete",
            ]
        )
        if agent_id == "supervisor" and is_action:
            require_approval = "approval" in lower_msg or "approve" in lower_msg
            threading.Thread(
                target=self.run_feature_workflow_sync,
                args=(
                    WorkflowTriggerRequest(
                        feature_description=req.message,
                        project_path=req.project_path,
                        require_approval=require_approval,
                    ),
                ),
                daemon=True,
            ).start()
            reply = (
                f"SupervisorAgent started the autonomous multi-agent workflow for: '{req.message}'.\n"
                "Pipeline: Supervisor -> ProjectAnalyzer -> Planner -> Developer -> CodeReviewer -> QAAgent (with Debugger auto-retry)."
            )
            self.update_agent_state(
                "supervisor",
                task=f"Orchestrating workflow: {req.message[:60]}",
                needs_input=False,
                working=True,
                add_tokens=200,
            )
            return {"agentId": agent_id, "success": True, "reply": reply, "state": self.agent_states[agent_id]}

        resolved_path = _resolve_game_project_path(req.project_path)

        # Otherwise run individual agent task
        self.update_agent_state(
            agent_id,
            task=f"Running: {req.message[:70]}",
            needs_input=False,
            working=True,
        )
        task = Task(
            title=f"Studio Directive for {agent.config.name}",
            description=(
                f"{req.message}\n\n"
                f"Target Game Project Directory: {resolved_path}\n"
                "Start by running `project_tree` or `list_files` on that exact directory."
            ),
            engine=req.engine,
            priority=TaskPriority.HIGH,
            context={"project_root": str(resolved_path)},
        )
        res = agent.run(task)
        reply_text = res.output if res.success else f"Error: {res.error}"
        est_tokens = max(450, len(reply_text) // 3 + len(req.message))

        self.update_agent_state(
            agent_id,
            task=f"Completed: {req.message[:60]}" if res.success else f"Failed: {res.error}",
            needs_input=False,
            working=False,
            add_tokens=est_tokens,
        )
        return {
            "agentId": agent_id,
            "success": res.success,
            "reply": reply_text,
            "files_created": res.files_created,
            "files_modified": res.files_modified,
            "state": self.agent_states[agent_id],
        }

    def run_feature_workflow_sync(self, req: WorkflowTriggerRequest) -> dict[str, Any]:
        """Execute FeatureDevelopmentWorkflow while streaming live node events to the 3D Office."""

        def approval_gate_callback(plan_text: str) -> bool:
            self._approval_event.clear()
            self._pending_approval = True
            self.update_agent_state(
                "planner",
                task="APPROVAL GATE: Waiting for Director to approve implementation plan",
                needs_input=True,
                working=False,
                chat_message={
                    "sender": "PlannerAgent",
                    "role": "agent",
                    "text": f"Approval Gate reached! Here is the plan:\n\n{plan_text[:900]}\n\nClick 'Approve plan & start Developer' or reply to continue.",
                },
            )
            self._approval_event.wait(timeout=600)
            return self._approval_decision

        wf = FeatureDevelopmentWorkflow(approval_callback=approval_gate_callback)
        # Attach live terminal event streaming to workflow's agents
        wf.supervisor.on_event = self._make_event_handler("supervisor")
        wf.project_analyzer.on_event = self._make_event_handler("project_analyzer")
        wf.planner.on_event = self._make_event_handler("planner")
        wf.developer.on_event = self._make_event_handler("developer")
        wf.code_reviewer.on_event = self._make_event_handler("code_reviewer")
        wf.qa_agent.on_event = self._make_event_handler("qa_agent")
        wf.debugger.on_event = self._make_event_handler("debugger")

        # Stream LangGraph node execution so each 3D employee lights up as they work
        resolved_path = _resolve_game_project_path(req.project_path)
        initial_state = {
            "user_request": req.feature_description,
            "project_path": str(resolved_path),
            "supervisor_brief": "",
            "analysis_report": "",
            "engine_name": "custom",
            "manifest": {},
            "skills_and_rules": "",
            "plan": "",
            "require_approval": req.require_approval,
            "approved": not req.require_approval,
            "approval_feedback": "",
            "developer_output": "",
            "code_review": "",
            "qa_report": "",
            "tests_passed": False,
            "debug_notes": "",
            "debug_attempts": 0,
            "max_debug_attempts": req.max_debug_attempts,
            "files_created": [],
            "files_modified": [],
            "steps": [],
            "final_report": "",
        }

        node_to_agent = {
            "supervisor": "supervisor",
            "project_analyzer": "project_analyzer",
            "planner": "planner",
            "developer": "developer",
            "code_reviewer": "code_reviewer",
            "qa_agent": "qa_agent",
            "debugger": "debugger",
        }

        last_state: dict[str, Any] = dict(initial_state)
        try:
            for event in wf.graph.stream(initial_state):
                for node_name, node_output in event.items():
                    last_state.update(node_output)
                    agent_id = node_to_agent.get(node_name)
                    if agent_id:
                        steps = node_output.get("steps", [])
                        last_step_out = steps[-1]["output"] if steps else f"Completed {node_name}"
                        self.update_agent_state(
                            agent_id,
                            task=f"Finished {node_name} step",
                            needs_input=False,
                            working=False,
                            add_tokens=max(600, len(str(last_step_out)) // 3),
                            chat_message={
                                "sender": self.agents[agent_id].config.name,
                                "role": "agent",
                                "text": str(last_step_out)[:1000],
                            },
                        )
                    self._emit_sync({"type": "workflow_step", "node": node_name, "engine": last_state.get("engine_name")})

            self._emit_sync(
                {
                    "type": "workflow_complete",
                    "success": last_state.get("tests_passed", False),
                    "summary": last_state.get("final_report", ""),
                    "filesCreated": last_state.get("files_created", []),
                    "filesModified": last_state.get("files_modified", []),
                }
            )
            return {"success": True, "final_report": last_state.get("final_report", "")}
        except Exception as e:
            self._emit_sync({"type": "workflow_error", "error": str(e)})
            return {"success": False, "error": str(e)}


bridge = StudioOrchestratorBridge()
app = FastAPI(title="GAME_AGENTS 3D Studio Real-Time API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    bridge.loop = asyncio.get_running_loop()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "game-agents-studio-bridge"}


@app.get("/api/agents/status")
async def get_agents_status() -> dict[str, Any]:
    return {"agents": list(bridge.agent_states.values()), "pendingApproval": bridge._pending_approval}


@app.post("/api/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, req: ChatRequest) -> dict[str, Any]:
    return await asyncio.to_thread(bridge.handle_agent_chat_sync, agent_id, req)


@app.post("/api/workflows/feature")
async def trigger_feature_workflow(req: WorkflowTriggerRequest) -> dict[str, Any]:
    threading.Thread(target=bridge.run_feature_workflow_sync, args=(req,), daemon=True).start()
    return {"status": "started", "feature": req.feature_description}


@app.post("/api/workflows/approval")
async def submit_approval(req: ApprovalDecisionRequest) -> dict[str, Any]:
    bridge._approval_decision = req.approved
    bridge._pending_approval = False
    bridge._approval_event.set()
    bridge.update_agent_state(
        "planner",
        task="Approved by Director" if req.approved else "Rejected by Director",
        needs_input=False,
        working=False,
    )
    return {"status": "ok", "approved": req.approved}


@app.websocket("/ws/studio")
async def studio_websocket(websocket: WebSocket) -> None:
    await bridge.ws_manager.connect(websocket)
    try:
        # Send initial snapshot of all agent states
        await websocket.send_json({"type": "snapshot", "agents": list(bridge.agent_states.values())})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        bridge.ws_manager.disconnect(websocket)


def main() -> None:
    import uvicorn

    uvicorn.run("game_agents.interfaces.api.server:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
