"""Unreal Engine-specific agent tools."""

import json
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class UnrealInspectUprojectInput(BaseModel):
    project_path: str = Field(default=".", description="Path to Unreal Engine project root")


class UnrealInspectUprojectTool(BaseTool):
    name: str = "unreal_inspect_uproject"
    description: str = "Inspect .uproject configuration: EngineAssociation, target modules, and enabled plugins."
    args_schema: type[BaseModel] = UnrealInspectUprojectInput

    def execute(self, project_path: str = ".") -> ToolResult:
        p = Path(project_path).resolve()
        uprojects = list(p.glob("*.uproject"))
        if not uprojects:
            return ToolResult(tool_name=self.name, success=False, error=f"No .uproject found in {project_path}")

        target = uprojects[0]
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            engine_ver = data.get("EngineAssociation", "Unknown")
            modules = [m.get("Name") for m in data.get("Modules", [])]
            plugins = [pl.get("Name") for pl in data.get("Plugins", []) if pl.get("Enabled", True)]

            output = [
                f"Project: {target.name}",
                f"Unreal Engine Association: {engine_ver}",
                f"C++ Modules: {', '.join(modules) if modules else 'Blueprint-only'}",
                f"Enabled Plugins: {', '.join(plugins) if plugins else 'None explicitly listed'}",
            ]
            return ToolResult(tool_name=self.name, success=True, output="\n".join(output), data=data)
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to parse {target.name}: {str(e)}")


class UnrealListPluginsInput(BaseModel):
    project_path: str = Field(default=".", description="Path to Unreal Engine project root")


class UnrealListPluginsTool(BaseTool):
    name: str = "unreal_list_plugins"
    description: str = "List plugins located in the project's Plugins/ folder."
    args_schema: type[BaseModel] = UnrealListPluginsInput

    def execute(self, project_path: str = ".") -> ToolResult:
        plugins_dir = Path(project_path).resolve() / "Plugins"
        if not plugins_dir.exists():
            return ToolResult(tool_name=self.name, success=True, output="No custom Plugins/ directory found.")

        uplugins = list(plugins_dir.rglob("*.uplugin"))
        if not uplugins:
            return ToolResult(tool_name=self.name, success=True, output="No .uplugin files in Plugins/ directory.")

        lines = [f"- {up.stem} ({up.relative_to(plugins_dir)})" for up in uplugins]
        return ToolResult(tool_name=self.name, success=True, output="Project Plugins:\n" + "\n".join(lines))
