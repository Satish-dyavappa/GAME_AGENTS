"""Feature Development Workflow: LangGraph StateGraph matching the full multi-agent pipeline.

Flow:
User Request -> Supervisor -> Project Analyzer -> Engine Resolver -> Load Skills and Rules -> Planner
  -> Approval Required?
       ├── Yes -> Human Approval -> Universal Developer
       └── No  -> Universal Developer
  -> Code Reviewer -> QA Agent -> Tests Passed?
       ├── Yes -> Final Report
       └── No  -> Debugger -> Universal Developer (retry loop)
"""

import time
from pathlib import Path
from typing import Any, Callable, TypedDict
from langgraph.graph import END, START, StateGraph

from game_agents.agents.analysis.project_analyzer import ProjectAnalyzerAgent
from game_agents.agents.development.code_reviewer import CodeReviewerAgent
from game_agents.agents.development.debugger import DebuggerAgent
from game_agents.agents.development.developer import DeveloperAgent
from game_agents.agents.orchestration.planner import PlannerAgent
from game_agents.agents.orchestration.supervisor import SupervisorAgent
from game_agents.agents.testing.qa_agent import QAAgent
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.task import Task, TaskPriority
from game_agents.engines.registry import EngineRegistry, default_engine_registry
from game_agents.skills.loader import SkillsAndRulesLoader
from game_agents.workflows.base_workflow import (
    BaseWorkflow,
    WorkflowResult,
    WorkflowStepResult,
)


class WorkflowGraphState(TypedDict):
    """Shared state passed between LangGraph nodes."""

    user_request: str
    project_path: str
    supervisor_brief: str
    analysis_report: str
    engine_name: str
    manifest: dict[str, Any]
    skills_and_rules: str
    plan: str
    require_approval: bool
    approved: bool
    approval_feedback: str
    developer_output: str
    code_review: str
    qa_report: str
    tests_passed: bool
    debug_notes: str
    debug_attempts: int
    max_debug_attempts: int
    files_created: list[str]
    files_modified: list[str]
    steps: list[dict[str, Any]]
    final_report: str


class FeatureDevelopmentWorkflow(BaseWorkflow):
    """LangGraph-powered multi-agent workflow with approval gate and debug retry loop."""

    name = "feature_development"
    description = (
        "Supervisor -> Project Analyzer -> Engine Resolver -> Skills/Rules -> Planner "
        "-> [Approval Gate] -> Developer -> Code Reviewer -> QA Agent -> [Debug Loop] -> Final Report."
    )

    def __init__(
        self,
        engine_registry: EngineRegistry | None = None,
        skills_loader: SkillsAndRulesLoader | None = None,
        approval_callback: Callable[[str], bool] | None = None,
    ) -> None:
        self.engine_registry = engine_registry or default_engine_registry
        self.skills_loader = skills_loader or SkillsAndRulesLoader()
        self.approval_callback = approval_callback

        # Initialize specialized agents
        self.supervisor = SupervisorAgent()
        self.project_analyzer = ProjectAnalyzerAgent()
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()
        self.code_reviewer = CodeReviewerAgent()
        self.qa_agent = QAAgent()
        self.debugger = DebuggerAgent()

        self.graph = self.build_graph()

    # ------------------------------------------------------------------
    # Graph Nodes
    # ------------------------------------------------------------------

    def _node_supervisor(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        task = Task(
            title="Supervisor Kickoff",
            description=(
                f"Evaluate the user request: '{state['user_request']}' for project '{state['project_path']}'. "
                "Provide a concise directive summarizing objectives and quality criteria."
            ),
            priority=TaskPriority.HIGH,
        )
        res = self.supervisor.run(task)
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="supervisor",
                agent_name=self.supervisor.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"supervisor_brief": res.output, "steps": steps}

    def _node_project_analyzer(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        p = Path(state["project_path"]).resolve()
        p.mkdir(parents=True, exist_ok=True)
        task = Task(
            title="Analyze Target Project",
            description=f"Inspect project directory '{p}' for existing files, scenes, dependencies, and structure.",
            priority=TaskPriority.MEDIUM,
        )
        res = self.project_analyzer.run(task)
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="project_analyzer",
                agent_name=self.project_analyzer.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"analysis_report": res.output, "steps": steps}

    def _node_engine_resolver(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        p = Path(state["project_path"]).resolve()
        adapter = self.engine_registry.detect(p)

        if adapter:
            manifest = adapter.inspect(p)
        else:
            # Infer engine from user prompt if workspace is new/empty
            req_lower = state["user_request"].lower()
            detected_type = EngineType.CUSTOM
            for eng in [EngineType.PHASER, EngineType.UNITY, EngineType.UNREAL, EngineType.THREEJS, EngineType.GODOT]:
                if eng.value in req_lower:
                    detected_type = eng
                    break
            manifest = ProjectManifest(
                name=p.name,
                root_path=p,
                engine=detected_type,
                entry_point="index.html" if detected_type in (EngineType.PHASER, EngineType.THREEJS) else None,
            )

        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="engine_resolver",
                agent_name="engine_registry",
                success=True,
                output=f"Resolved engine: {manifest.engine.value}",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {
            "engine_name": manifest.engine.value,
            "manifest": manifest.model_dump(mode="json"),
            "steps": steps,
        }

    def _node_load_skills_and_rules(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        engine = state.get("engine_name", "custom")
        context_text = self.skills_loader.format_context(engine)

        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="load_skills_and_rules",
                agent_name="skills_loader",
                success=True,
                output=f"Loaded skills and rules for '{engine}' ({len(context_text)} chars).",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"skills_and_rules": context_text, "steps": steps}

    def _node_planner(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        manifest = ProjectManifest(**state["manifest"])
        task = Task(
            title=f"Plan: {state['user_request'][:50]}",
            description=(
                f"User Request: {state['user_request']}\n"
                f"Supervisor Directive: {state.get('supervisor_brief', '')}\n"
                f"Project Analysis: {state.get('analysis_report', '')}\n\n"
                f"Follow these Rules & Skills:\n{state.get('skills_and_rules', '')}\n\n"
                "Create a detailed, step-by-step implementation plan."
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        res = self.planner.run(task, manifest=manifest)
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="planner",
                agent_name=self.planner.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"plan": res.output, "steps": steps}

    def _node_human_approval(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        plan_text = state.get("plan", "")
        if self.approval_callback:
            approved = bool(self.approval_callback(plan_text))
            feedback = "Approved via callback." if approved else "Rejected via callback."
        else:
            approved = True
            feedback = "Auto-approved (no interactive callback provided)."

        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="human_approval",
                agent_name="human_gate",
                success=approved,
                output=feedback,
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"approved": approved, "approval_feedback": feedback, "steps": steps}

    def _node_developer(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        manifest = ProjectManifest(**state["manifest"])
        debug_notes = state.get("debug_notes", "")

        desc_parts = [
            f"Implement the requested game feature in '{state['project_path']}'.",
            f"User Request: {state['user_request']}",
            f"Implementation Plan:\n{state.get('plan', '')}",
            f"Rules & Skills:\n{state.get('skills_and_rules', '')}",
        ]
        if debug_notes:
            desc_parts.append(
                f"IMPORTANT - Fix ALL remaining errors identified by Debugger/QA:\n{debug_notes}\n\n"
                "Apply every fix using `edit_file` / `write_file`, then run the build/test command via `execute_command` to confirm zero errors."
            )

        task = Task(
            title=f"Develop: {state['user_request'][:50]}",
            description="\n\n".join(desc_parts),
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        res = self.developer.run(task, manifest=manifest)

        created = list(set(state.get("files_created", []) + res.files_created))
        modified = list(set(state.get("files_modified", []) + res.files_modified))
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="developer",
                agent_name=self.developer.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {
            "developer_output": res.output,
            "files_created": created,
            "files_modified": modified,
            "steps": steps,
        }

    def _node_code_reviewer(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        manifest = ProjectManifest(**state["manifest"])
        task = Task(
            title="Review Implemented Code",
            description=(
                f"Review code in '{state['project_path']}' against these standards:\n"
                f"{state.get('skills_and_rules', '')}"
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.MEDIUM,
        )
        res = self.code_reviewer.run(task, manifest=manifest)
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="code_reviewer",
                agent_name=self.code_reviewer.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"code_review": res.output, "steps": steps}

    def _node_qa_agent(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        manifest = ProjectManifest(**state["manifest"])
        task = Task(
            title="QA Verification & Tests",
            description=(
                f"Verify project '{state['project_path']}'. Run tests, check for syntax/runtime errors, "
                "and confirm the feature works. Start your final verdict with 'PASS:' or 'FAIL:'."
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        res = self.qa_agent.run(task, manifest=manifest)
        out_lower = (res.output or "").lower()
        passed = res.success and not out_lower.startswith("fail")

        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="qa_agent",
                agent_name=self.qa_agent.config.name,
                success=passed,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {"qa_report": res.output, "tests_passed": passed, "steps": steps}

    def _node_debugger(self, state: WorkflowGraphState) -> dict[str, Any]:
        t0 = time.time()
        manifest = ProjectManifest(**state["manifest"])
        attempts = state.get("debug_attempts", 0) + 1
        task = Task(
            title=f"Debug & Fix Failures (Attempt {attempts})",
            description=(
                f"QA reported failures in '{state['project_path']}':\n{state.get('qa_report', '')}\n\n"
                "Diagnose the root cause AND apply fixes directly using `edit_file` / `write_file` where possible. "
                "List any remaining steps clearly so DeveloperAgent can finish and verify."
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.CRITICAL,
        )
        res = self.debugger.run(task, manifest=manifest)
        modified = list(set(state.get("files_modified", []) + res.files_modified))
        steps = list(state.get("steps", []))
        steps.append(
            WorkflowStepResult(
                step_name="debugger",
                agent_name=self.debugger.config.name,
                success=res.success,
                output=res.output or res.error or "",
                duration_seconds=round(time.time() - t0, 2),
            ).model_dump()
        )
        return {
            "debug_notes": res.output,
            "debug_attempts": attempts,
            "files_modified": modified,
            "steps": steps,
        }

    def _node_final_report(self, state: WorkflowGraphState) -> dict[str, Any]:
        status_str = "PASSED" if state.get("tests_passed", False) else "COMPLETED WITH WARNINGS"
        report = (
            f"# Final Workflow Report ({status_str})\n"
            f"- **Request:** {state['user_request']}\n"
            f"- **Engine:** {state.get('engine_name', 'custom')}\n"
            f"- **Files Created:** {len(state.get('files_created', []))}\n"
            f"- **Files Modified:** {len(state.get('files_modified', []))}\n"
            f"- **Debug Retries:** {state.get('debug_attempts', 0)}\n\n"
            f"## QA Summary\n{state.get('qa_report', 'N/A')}"
        )
        return {"final_report": report}

    # ------------------------------------------------------------------
    # Conditional Edge Routers
    # ------------------------------------------------------------------

    @staticmethod
    def _route_approval(state: WorkflowGraphState) -> str:
        return "yes" if state.get("require_approval", False) else "no"

    @staticmethod
    def _route_after_approval(state: WorkflowGraphState) -> str:
        return "approved" if state.get("approved", True) else "rejected"

    @staticmethod
    def _route_after_qa(state: WorkflowGraphState) -> str:
        if state.get("tests_passed", False):
            return "yes"
        if state.get("debug_attempts", 0) < state.get("max_debug_attempts", 2):
            return "no"
        return "yes"  # Max debug retries reached -> proceed to Final Report

    # ------------------------------------------------------------------
    # Graph Construction
    # ------------------------------------------------------------------

    def build_graph(self) -> Any:
        """Assemble and compile the LangGraph StateGraph matching the flowchart."""
        builder = StateGraph(WorkflowGraphState)

        builder.add_node("supervisor", self._node_supervisor)
        builder.add_node("project_analyzer", self._node_project_analyzer)
        builder.add_node("engine_resolver", self._node_engine_resolver)
        builder.add_node("load_skills_and_rules", self._node_load_skills_and_rules)
        builder.add_node("planner", self._node_planner)
        builder.add_node("human_approval", self._node_human_approval)
        builder.add_node("developer", self._node_developer)
        builder.add_node("code_reviewer", self._node_code_reviewer)
        builder.add_node("qa_agent", self._node_qa_agent)
        builder.add_node("debugger", self._node_debugger)
        builder.add_node("final_report", self._node_final_report)

        # Sequential flow
        builder.add_edge(START, "supervisor")
        builder.add_edge("supervisor", "project_analyzer")
        builder.add_edge("project_analyzer", "engine_resolver")
        builder.add_edge("engine_resolver", "load_skills_and_rules")
        builder.add_edge("load_skills_and_rules", "planner")

        # Approval Gate
        builder.add_conditional_edges(
            "planner",
            self._route_approval,
            {"yes": "human_approval", "no": "developer"},
        )
        builder.add_conditional_edges(
            "human_approval",
            self._route_after_approval,
            {"approved": "developer", "rejected": "final_report"},
        )

        # Implementation -> Review -> QA
        builder.add_edge("developer", "code_reviewer")
        builder.add_edge("code_reviewer", "qa_agent")

        # QA Gate -> Final Report OR Debugger -> Developer loop
        builder.add_conditional_edges(
            "qa_agent",
            self._route_after_qa,
            {"yes": "final_report", "no": "debugger"},
        )
        builder.add_edge("debugger", "developer")
        builder.add_edge("final_report", END)

        return builder.compile()

    def get_graph_mermaid(self) -> str:
        """Return Mermaid diagram syntax of the compiled LangGraph workflow."""
        return self.graph.get_graph().draw_mermaid()

    def run(
        self,
        feature_description: str,
        project_path: str = ".",
        require_approval: bool = False,
        max_debug_attempts: int = 2,
    ) -> WorkflowResult:
        """Execute the full LangGraph workflow."""
        start_time = time.time()
        initial_state: WorkflowGraphState = {
            "user_request": feature_description,
            "project_path": str(Path(project_path).resolve()),
            "supervisor_brief": "",
            "analysis_report": "",
            "engine_name": "custom",
            "manifest": {},
            "skills_and_rules": "",
            "plan": "",
            "require_approval": require_approval,
            "approved": not require_approval,
            "approval_feedback": "",
            "developer_output": "",
            "code_review": "",
            "qa_report": "",
            "tests_passed": False,
            "debug_notes": "",
            "debug_attempts": 0,
            "max_debug_attempts": max_debug_attempts,
            "files_created": [],
            "files_modified": [],
            "steps": [],
            "final_report": "",
        }

        final_state = self.graph.invoke(initial_state)
        total_time = round(time.time() - start_time, 2)
        step_models = [WorkflowStepResult(**s) for s in final_state.get("steps", [])]

        return WorkflowResult(
            workflow_name=self.name,
            success=final_state.get("tests_passed", False),
            summary=final_state.get("final_report", ""),
            steps=step_models,
            files_created=final_state.get("files_created", []),
            files_modified=final_state.get("files_modified", []),
            artifacts={
                "manifest": final_state.get("manifest", {}),
                "plan": final_state.get("plan", ""),
                "code_review": final_state.get("code_review", ""),
                "qa_report": final_state.get("qa_report", ""),
                "debug_attempts": final_state.get("debug_attempts", 0),
            },
            total_duration_seconds=total_time,
        )
