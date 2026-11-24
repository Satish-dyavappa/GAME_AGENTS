"""Configuration schema for game dev agents."""

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration profile defining an agent's persona, allowed tools, and model settings."""

    name: str = Field(..., description="Unique agent identifier (e.g. 'supervisor', 'developer')")
    role: str = Field(..., description="Agent role title (e.g. 'Universal Game Developer')")
    system_prompt: str = Field(..., description="Core persona, rules, and system prompt instructions")
    tools: list[str] = Field(default_factory=list, description="Names of tools this agent is permitted to execute")
    model_provider: str | None = Field(default=None, description="Optional override for model provider")
    model_name: str | None = Field(default=None, description="Optional override for model name")
    max_iterations: int = Field(default=15, description="Max tool execution iterations before forcing completion")
    temperature: float = Field(default=0.2, description="Sampling temperature")
