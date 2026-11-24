"""Base Engine Adapter defining standard capabilities across all game engines."""

from abc import ABC, abstractmethod
from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class BaseEngineAdapter(ABC):
    """Abstract adapter bridging the AI framework to a specific game engine.

    Handles project inspection, editor integration, building, testing, and validation.
    """

    engine_type: EngineType
    name: str

    @abstractmethod
    def detect(self, project_path: Path) -> bool:
        """Detect if the target directory contains a project for this engine."""
        pass

    @abstractmethod
    def inspect(self, project_path: Path) -> ProjectManifest:
        """Extract and return full project metadata, version, entry point, and structure."""
        pass

    @abstractmethod
    def build(self, project_path: Path) -> ToolResult:
        """Execute compilation, bundler, or build pipeline for this engine."""
        pass

    @abstractmethod
    def test(self, project_path: Path) -> ToolResult:
        """Run engine-specific automated unit or gameplay tests."""
        pass

    @abstractmethod
    def validate(self, project_path: Path) -> ToolResult:
        """Audit project files, configs, and scenes for integrity and engine standards."""
        pass

    def get_tools(self) -> list[BaseTool]:
        """Return engine-specific tools to register with agents."""
        return []
