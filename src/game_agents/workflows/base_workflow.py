"""Base workflow abstractions for multi-agent game dev pipelines."""

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    """Execution state of a workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStepResult(BaseModel):
    """Result of an individual agent step in the workflow pipeline."""

    step_name: str = Field(..., description="Name of the workflow step (e.g. 'planning', 'coding')")
    agent_name: str = Field(..., description="Agent that executed this step")
    success: bool = Field(default=True, description="Whether the step succeeded")
    output: str = Field(..., description="Summary of the step execution")
    duration_seconds: float = Field(default=0.0, description="Step execution time")


class WorkflowResult(BaseModel):
    """Complete summary of a workflow execution across all agent steps."""

    workflow_name: str = Field(..., description="Name of the workflow")
    success: bool = Field(default=True, description="Overall pipeline success")
    summary: str = Field(..., description="Executive summary of the completed workflow")
    steps: list[WorkflowStepResult] = Field(default_factory=list, description="Ordered step execution results")
    files_created: list[str] = Field(default_factory=list, description="All files created during workflow")
    files_modified: list[str] = Field(default_factory=list, description="All files modified during workflow")
    artifacts: dict[str, Any] = Field(default_factory=dict, description="Structured artifacts produced")
    total_duration_seconds: float = Field(default=0.0, description="Total execution time")
    error: str | None = Field(default=None, description="Pipeline failure error message if any")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseWorkflow(ABC):
    """Abstract base class for orchestrating multi-agent game development workflows."""

    name: str
    description: str

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> WorkflowResult:
        """Execute the multi-agent pipeline."""
        pass
