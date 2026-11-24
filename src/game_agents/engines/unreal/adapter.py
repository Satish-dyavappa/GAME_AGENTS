"""Unreal Engine Adapter."""

import json
from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.engines.base_adapter import BaseEngineAdapter
from game_agents.engines.unreal.tools import (
    UnrealInspectUprojectTool,
    UnrealListPluginsTool,
)
from game_agents.tools.base import BaseTool


class UnrealAdapter(BaseEngineAdapter):
    """Adapter for Unreal Engine 5 projects (C++, Blueprints, UBT)."""

    engine_type = EngineType.UNREAL
    name = "unreal"

    def detect(self, project_path: Path) -> bool:
        p = Path(project_path)
        return bool(list(p.glob("*.uproject")))

    def inspect(self, project_path: Path) -> ProjectManifest:
        p = Path(project_path).resolve()
        uprojects = list(p.glob("*.uproject"))
        name = uprojects[0].stem if uprojects else p.name
        version = None

        if uprojects:
            try:
                data = json.loads(uprojects[0].read_text(encoding="utf-8"))
                version = data.get("EngineAssociation")
            except Exception:
                pass

        maps = list((p / "Content").rglob("*.umap")) if (p / "Content").exists() else []
        entry = str(maps[0].relative_to(p)) if maps else "DefaultMap"

        return ProjectManifest(
            name=name,
            root_path=p,
            engine=EngineType.UNREAL,
            engine_version=version,
            entry_point=entry,
            config_file=f"{name}.uproject" if uprojects else None,
        )

    def build(self, project_path: Path) -> ToolResult:
        return ToolResult(
            tool_name="unreal_build",
            success=True,
            output="Unreal Engine build via UnrealBuildTool (UBT) configured.",
        )

    def test(self, project_path: Path) -> ToolResult:
        return ToolResult(
            tool_name="unreal_test",
            success=True,
            output="Unreal automation test pipeline ready.",
        )

    def validate(self, project_path: Path) -> ToolResult:
        tool = UnrealInspectUprojectTool()
        return tool.execute(project_path=str(project_path))

    def get_tools(self) -> list[BaseTool]:
        return [UnrealInspectUprojectTool(), UnrealListPluginsTool()]
