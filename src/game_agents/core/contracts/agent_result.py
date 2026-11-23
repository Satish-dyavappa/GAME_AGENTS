"""Agent result contract."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Standardized output returned by an agent upon task execution."""

    task_id: str = Field(..., description="ID of the task that was executed")
    agent_name: str = Field(..., description="Name or role of the agent that produced this result")
    success: bool = Field(default=True, description="Whether the task succeeded")
    output: str = Field(..., description="Text summary or response of the execution")
    files_created: list[str] = Field(default_factory=list, description="Files created by the agent")
    files_modified: list[str] = Field(default_factory=list, description="Files modified by the agent")
    artifacts: dict[str, Any] = Field(default_factory=dict, description="Structured artifacts generated (e.g. AST, scene trees)")
    error: str | None = Field(default=None, description="Error details if execution failed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
