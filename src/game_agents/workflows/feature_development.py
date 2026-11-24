"""Feature Development Workflow: End-to-end multi-agent feature implementation pipeline."""

import time
from pathlib import Path
from typing import Any
from game_agents.agents.development.code_reviewer import CodeReviewerAgent
from game_agents.agents.development.debugger import DebuggerAgent
from game_agents.agents.development.developer import DeveloperAgent
from game_agents.agents.orchestration.planner import PlannerAgent
from game_agents.agents.testing.qa_agent import QAAgent
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.task import Task, TaskPriority
from game_agents.engines.registry import EngineRegistry, default_engine_registry
from game_agents.workflows.base_workflow import (
    BaseWorkflow,
    WorkflowResult,
    WorkflowStepResult,
)


class FeatureDevelopmentWorkflow(BaseWorkflow):
    """Multi-agent pipeline: Feature Planning -> Development -> Code Review -> QA Verification (with Auto-Debug)."""

    name = "feature_development"
    description = "Plan, implement, review, and test a game feature with autonomous multi-agent handoffs."

    def __init__(self, engine_registry: EngineRegistry | None = None) -> None:
        self.engine_registry = engine_registry or default_engine_registry
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()
        self.code_reviewer = CodeReviewerAgent()
        self.qa_agent = QAAgent()
        self.debugger = DebuggerAgent()

    def run(
        self,
        feature_description: str,
        project_path: str = ".",
        max_fix_retries: int = 1,
    ) -> WorkflowResult:
        start_time = time.time()
        p = Path(project_path).resolve()
        steps: list[WorkflowStepResult] = []
        files_created: set[str] = set()
        files_modified: set[str] = set()
        artifacts: dict[str, Any] = {}

        # 1. Resolve Target Engine
        adapter = self.engine_registry.detect(p)
        manifest = adapter.inspect(p) if adapter else ProjectManifest(
            name=p.name,
            root_path=p,
            engine=EngineType.CUSTOM,
            entry_point="index.html" if (p / "index.html").exists() else "main.py",
        )

        # 2. Planning Step
        t0 = time.time()
        plan_task = Task(
            title=f"Plan Feature: {feature_description[:60]}",
            description=f"Produce an atomic implementation plan for feature: '{feature_description}' in {manifest.engine.value}.",
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        plan_res = self.planner.run(plan_task, manifest=manifest)
        steps.append(
            WorkflowStepResult(
                step_name="planning",
                agent_name=self.planner.config.name,
                success=plan_res.success,
                output=plan_res.output,
                duration_seconds=round(time.time() - t0, 2),
            )
        )
        artifacts["plan"] = plan_res.output

        if not plan_res.success:
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                summary="Planning phase failed.",
                steps=steps,
                error=plan_res.error,
                total_duration_seconds=round(time.time() - start_time, 2),
            )

        # 3. Development / Coding Step
        t1 = time.time()
        dev_task = Task(
            title=f"Implement Feature: {feature_description[:60]}",
            description=(
                f"Implement the feature based on the following plan:\n\n{plan_res.output}\n\n"
                f"Feature Requirement: {feature_description}\n"
                f"Engine: {manifest.engine.value}. Write clean, modular code and update all necessary scene/script files."
            ),
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        dev_res = self.developer.run(dev_task, manifest=manifest)
        files_created.update(dev_res.files_created)
        files_modified.update(dev_res.files_modified)
        steps.append(
            WorkflowStepResult(
                step_name="development",
                agent_name=self.developer.config.name,
                success=dev_res.success,
                output=dev_res.output,
                duration_seconds=round(time.time() - t1, 2),
            )
        )
        artifacts["developer_output"] = dev_res.output

        # 4. Code Review Step
        t2 = time.time()
        review_task = Task(
            title="Review Game Feature Code",
            description=f"Review changes made for feature '{feature_description}'. Check performance, memory leaks, and engine idioms.",
            engine=manifest.engine.value,
            priority=TaskPriority.MEDIUM,
        )
        review_res = self.code_reviewer.run(review_task, manifest=manifest)
        steps.append(
            WorkflowStepResult(
                step_name="code_review",
                agent_name=self.code_reviewer.config.name,
                success=review_res.success,
                output=review_res.output,
                duration_seconds=round(time.time() - t2, 2),
            )
        )
        artifacts["code_review"] = review_res.output

        # 5. QA Verification Step
        t3 = time.time()
        qa_task = Task(
            title="Verify Feature Tests & Build",
            description=f"Verify project build and run tests for '{manifest.name}'. Check for compile/runtime errors.",
            engine=manifest.engine.value,
            priority=TaskPriority.HIGH,
        )
        qa_res = self.qa_agent.run(qa_task, manifest=manifest)
        steps.append(
            WorkflowStepResult(
                step_name="qa_verification",
                agent_name=self.qa_agent.config.name,
                success=qa_res.success,
                output=qa_res.output,
                duration_seconds=round(time.time() - t3, 2),
            )
        )
        artifacts["qa_report"] = qa_res.output

        # 6. Auto-Debug Recovery Loop if QA/Build encountered issues
        if not qa_res.success and max_fix_retries > 0:
            t4 = time.time()
            debug_task = Task(
                title="Fix QA Verification Errors",
                description=f"QA reported errors:\n{qa_res.output or qa_res.error}\nFix the offending files.",
                engine=manifest.engine.value,
                priority=TaskPriority.CRITICAL,
            )
            debug_res = self.debugger.run(debug_task, manifest=manifest)
            files_modified.update(debug_res.files_modified)
            steps.append(
                WorkflowStepResult(
                    step_name="auto_debug_fix",
                    agent_name=self.debugger.config.name,
                    success=debug_res.success,
                    output=debug_res.output,
                    duration_seconds=round(time.time() - t4, 2),
                )
            )

        total_time = round(time.time() - start_time, 2)
        all_ok = plan_res.success and dev_res.success

        summary = (
            f"Feature Development Complete for '{feature_description[:50]}'. "
            f"Created: {len(files_created)} files, Modified: {len(files_modified)} files. "
            f"Status: {'SUCCESS' if all_ok else 'FAILED'} ({total_time}s)"
        )

        return WorkflowResult(
            workflow_name=self.name,
            success=all_ok,
            summary=summary,
            steps=steps,
            files_created=list(files_created),
            files_modified=list(files_modified),
            artifacts=artifacts,
            total_duration_seconds=total_time,
        )
