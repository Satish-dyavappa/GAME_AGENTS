"""Registry for managing and discovering agent tools."""

from typing import Any
from game_agents.tools.base import BaseTool


class ToolRegistry:
    """Central catalog of tools available to agents."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._categories: dict[str, list[str]] = {}

    def register(self, tool: BaseTool, category: str = "general") -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        if category not in self._categories:
            self._categories[category] = []
        if tool.name not in self._categories[category]:
            self._categories[category].append(tool.name)

    def get(self, name: str) -> BaseTool | None:
        """Get tool by name."""
        return self._tools.get(name)

    def get_by_category(self, category: str) -> list[BaseTool]:
        """Return all tools in a specific category."""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_all(self) -> list[BaseTool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """Return all tools as OpenAI/OpenRouter function calling definitions."""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def to_langchain_tools(self) -> list[Any]:
        """Return all tools as LangChain tools."""
        return [tool.to_langchain_tool() for tool in self._tools.values() if tool.to_langchain_tool() is not None]


# Global tool registry instance
default_tool_registry = ToolRegistry()
