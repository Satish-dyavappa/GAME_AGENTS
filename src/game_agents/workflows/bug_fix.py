"""Bug Fix Workflow: Autonomous diagnostic, patch, and regression test pipeline."""

import time
from pathlib import Path
from typing import Any
from game_agents.agents.development.code_reviewer import CodeReviewerAgent
from game_agents.agents.development.debugger import DebuggerAgent
from game_agents.agents.testing.qa_agent import QAAgent
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.task import Task, TaskPriority
from game_agents.engines.registry import EngineRegistry, default_engine_registry
from game_agents.workflows.base_workflow import (
    BaseWorkflow,
    WorkflowResult,
    WorkflowStepResult,
)


class BugFixWorkflow(BaseWorkflow):
    """Autonomous Bug Fix Pipeline: Diagnose -> Surgical Patch -> Verify -> Review."""

    name = "bug_fix"
    description = "Diagnose runtime or compile errors, apply surgical fixes, and verify with QA."

    def __init__(self, engine_registry: EngineRegistry | None = None) -> None:
        self.engine_registry = engine_registry or default_engine_registry
        self.debugger = DebuggerAgent()
        self.qa_agent = QAAgent()
        self.code_reviewer = CodeReviewerAgent()

    def run(
        self,
        bug_report: str,
        project_path: str = ".",
        error_logs: str | None = None,
    ) -> WorkflowResult:
        start_time = time.time()
        p = Path(project_path).resolve()
        steps: list[WorkflowStepResult] = []
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

        # 2. Debugging & Patching Step
        t0 = time.time()
        diag_desc = [
            f"Fix the following game bug: '{bug_report}'",
            f"Target Engine: {manifest.engine.value}",
        ]
        if error_logs:
            diag_desc.append(f"Stack Trace / Logs:\n{error_logs}")

        debug_task = Task(
            title=f"Fix Bug: {bug_report[:60]}",
            description="\n".join(diag_desc),
            engine=manifest.engine.value,
            priority=TaskPriority.CRITICAL,
        )
        debug_res = self.debugger.run(debug_task, manifest=manifest)
        files_modified.update(debug_res.files_modified)
        steps.append(
            WorkflowStepResult(
                step_name="bug_diagnosis_and_patch",
                agent_name=self.debugger.config.name,
                success=debug_res.success,
                output=debug_res.output,
                duration_seconds=round(time.time() - t0, 2),
            )
        )
        artifacts["debug_output"] = debug_res.output

        if not debug_res.success:
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                summary=f"Bug fix failed during patching: {bug_report[:50]}",
                steps=steps,
                error=debug_res.error,
                total_duration_seconds=round(time.time() - start_time, 2),
            )

        # 3. QA Re-Verification Step
        t1 = time.time()
        qa_task = Task(
            title="Verify Bug Fix",
            description=f"Verify project build and run tests after fixing bug: '{bug_report}'. Ensure error is resolved.",
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
                duration_seconds=round(time.time() - t1, 2),
            )
        )
        artifacts["qa_report"] = qa_res.output

        # 4. Code Review Step to ensure no regressions
        t2 = time.time()
        review_task = Task(
            title="Review Bug Patch",
            description=f"Review git diff for bug fix: '{bug_report}'. Ensure patch is minimal and safe.",
            engine=manifest.engine.value,
            priority=TaskPriority.MEDIUM,
        )
        review_res = self.code_reviewer.run(review_task, manifest=manifest)
        steps.append(
            WorkflowStepResult(
                step_name="patch_review",
                agent_name=self.code_reviewer.config.name,
                success=review_res.success,
                output=review_res.output,
                duration_seconds=round(time.time() - t2, 2),
            )
        )
        artifacts["review_output"] = review_res.output

        total_time = round(time.time() - start_time, 2)
        summary = (
            f"Bug Fix Pipeline Completed for '{bug_report[:50]}'. "
            f"Modified: {len(files_modified)} files. "
            f"Status: {'SUCCESS' if debug_res.success else 'FAILED'} ({total_time}s)"
        )

        return WorkflowResult(
            workflow_name=self.name,
            success=debug_res.success,
            summary=summary,
            steps=steps,
            files_modified=list(files_modified),
            artifacts=artifacts,
            total_duration_seconds=total_time,
        )
