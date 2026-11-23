"""Base tool definition for game dev agents."""

from abc import ABC, abstractmethod
from typing import Any, Type
from pydantic import BaseModel
from game_agents.core.contracts.tool_result import ToolResult


class BaseTool(ABC, BaseModel):
    """Abstract base class for all tools available to game dev agents."""

    name: str
    description: str
    args_schema: Type[BaseModel] | None = None

    model_config = {"arbitrary_types_allowed": True}

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool logic and return a standardized ToolResult."""
        pass

    def __call__(self, **kwargs: Any) -> ToolResult:
        """Allow calling the tool instance directly."""
        try:
            if self.args_schema:
                validated_args = self.args_schema(**kwargs).model_dump()
                return self.execute(**validated_args)
            return self.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Error executing {self.name}: {str(e)}",
            )

    def to_openai_tool(self) -> dict[str, Any]:
        """Export tool definition in OpenAI / OpenRouter function calling format."""
        schema = self.args_schema.model_json_schema() if self.args_schema else {"type": "object", "properties": {}}
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }

    def to_langchain_tool(self) -> Any:
        """Convert to a LangChain StructuredTool for use in LangGraph / LangChain agents."""
        try:
            from langchain_core.tools import StructuredTool

            return StructuredTool.from_function(
                func=self.__call__,
                name=self.name,
                description=self.description,
                args_schema=self.args_schema,
            )
        except ImportError:
            return None
