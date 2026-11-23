"""Task contract and status definitions for game dev agents."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    """Lifecycle states of a task."""

    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Status alias for convenience
Status = TaskStatus


class TaskPriority(StrEnum):
    """Priority level for task execution."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Represents a discrete unit of game development work.

    Can represent high-level objectives (e.g., 'Implement player movement')
    or granular subtasks (e.g., 'Write PlayerController.cs').
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Short summary of the task")
    description: str = Field(..., description="Detailed instructions or prompt for the agent")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current execution state")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task urgency")

    # Engine and Agent routing
    engine: str | None = Field(default=None, description="Target game engine (e.g. phaser, unity, unreal, godot, web)")
    assigned_to: str | None = Field(default=None, description="Assigned agent role or name")

    # Dependencies & hierarchy
    parent_id: str | None = Field(default=None, description="Parent task ID if this is a subtask")
    dependencies: list[str] = Field(default_factory=list, description="List of task IDs that must complete before this runs")

    # Context & metadata
    context: dict[str, Any] = Field(default_factory=dict, description="Metadata, file paths, requirements, or scene references")
    result: Any | None = Field(default=None, description="Execution result or output from the agent")
    error: str | None = Field(default=None, description="Error message if the task failed")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Lifecycle state transition helpers
    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)

    def complete(self, result: Any = None) -> None:
        """Mark task as successfully completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        if result is not None:
            self.result = result

    def fail(self, error: str) -> None:
        """Mark task as failed with an error message."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error

    def cancel(self, reason: str | None = None) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
        if reason:
            self.error = f"Cancelled: {reason}"

    def is_finished(self) -> bool:
        """Return True if task has reached a terminal state."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)

    def is_ready(self, completed_ids: set[str]) -> bool:
        """Check if all prerequisite dependencies have completed."""
        return all(dep_id in completed_ids for dep_id in self.dependencies)
