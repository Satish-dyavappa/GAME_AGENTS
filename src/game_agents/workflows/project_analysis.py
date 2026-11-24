"""Project Analysis Workflow: Comprehensive scan, engine detection, and architecture report."""

import time
from pathlib import Path
from typing import Any
from game_agents.agents.analysis.project_analyzer import ProjectAnalyzerAgent
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.task import Task, TaskPriority
from game_agents.engines.registry import EngineRegistry, default_engine_registry
from game_agents.workflows.base_workflow import (
    BaseWorkflow,
    WorkflowResult,
    WorkflowStepResult,
)


class ProjectAnalysisWorkflow(BaseWorkflow):
    """Workflow that inspects a game codebase, detects its engine, and generates an architecture report."""

    name = "project_analysis"
    description = "Inspect repository, detect game engine, inspect scenes & assets, and produce architectural report."

    def __init__(self, engine_registry: EngineRegistry | None = None) -> None:
        self.engine_registry = engine_registry or default_engine_registry
        self.analyzer_agent = ProjectAnalyzerAgent()

    def run(self, project_path: str = ".") -> WorkflowResult:
        start_time = time.time()
        p = Path(project_path).resolve()
        steps: list[WorkflowStepResult] = []
        artifacts: dict[str, Any] = {}

        if not p.exists():
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                summary=f"Project directory does not exist: {project_path}",
                error="Path not found",
                total_duration_seconds=0.0,
            )

        # Step 1: Engine Detection & Inspection
        t0 = time.time()
        adapter = self.engine_registry.detect(p)
        if adapter:
            manifest = adapter.inspect(p)
            val_res = adapter.validate(p)
            step1_out = (
                f"Detected Engine: {adapter.name.title()} ({manifest.engine_version or 'unknown version'})\n"
                f"Entry Point: {manifest.entry_point}\n"
                f"Validation: {'PASSED' if val_res.success else 'WARNINGS: ' + str(val_res.error)}"
            )
        else:
            manifest = ProjectManifest(
                name=p.name,
                root_path=p,
                engine=EngineType.CUSTOM,
                entry_point="index.html" if (p / "index.html").exists() else "main.py",
            )
            step1_out = "Custom/Unknown game engine detected."

        steps.append(
            WorkflowStepResult(
                step_name="engine_detection",
                agent_name="engine_registry",
                success=True,
                output=step1_out,
                duration_seconds=round(time.time() - t0, 2),
            )
        )
        artifacts["manifest"] = manifest.model_dump(mode="json")

        # Step 2: In-Depth Architectural Analysis Agent
        t1 = time.time()
        task = Task(
            title=f"Analyze Game Architecture for {p.name}",
            description=(
                f"Inspect repository at '{p}'. Report on scene hierarchy, game objects, assets, "
                f"dependencies, and recommended architecture for game development."
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
            context={"project_root": str(p), "engine": manifest.engine.value},
        )

        agent_res = self.analyzer_agent.run(task, manifest=manifest)
        steps.append(
            WorkflowStepResult(
                step_name="architecture_analysis",
                agent_name=self.analyzer_agent.config.name,
                success=agent_res.success,
                output=agent_res.output if agent_res.success else agent_res.error or "Analysis failed",
                duration_seconds=round(time.time() - t1, 2),
            )
        )
        artifacts["analysis_output"] = agent_res.output

        total_time = round(time.time() - start_time, 2)
        summary = (
            f"Project Analysis Complete for '{manifest.name}' ({manifest.engine.value.title()}). "
            f"Execution time: {total_time}s."
        )

        return WorkflowResult(
            workflow_name=self.name,
            success=agent_res.success,
            summary=summary,
            steps=steps,
            artifacts=artifacts,
            total_duration_seconds=total_time,
        )
