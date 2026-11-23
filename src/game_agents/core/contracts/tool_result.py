"""Tool execution result contract."""

from typing import Any
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Standardized result returned by tool executions."""

    tool_name: str = Field(..., description="Name of the tool executed")
    success: bool = Field(default=True, description="Whether the tool execution succeeded")
    output: str = Field(default="", description="Standard output or formatted result")
    data: Any | None = Field(default=None, description="Raw structured data payload")
    error: str | None = Field(default=None, description="Error message if the tool failed")
