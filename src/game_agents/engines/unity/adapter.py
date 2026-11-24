"""Unity Engine Adapter."""

import re
from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.engines.base_adapter import BaseEngineAdapter
from game_agents.engines.unity.tools import (
    UnityCheckMetaFilesTool,
    UnityInspectVersionTool,
)
from game_agents.tools.base import BaseTool
from game_agents.tools.terminal.execute_command import ExecuteCommandTool


class UnityAdapter(BaseEngineAdapter):
    """Adapter for Unity projects (C#, Unity Editor, Package Manager)."""

    engine_type = EngineType.UNITY
    name = "unity"

    def detect(self, project_path: Path) -> bool:
        p = Path(project_path)
        return (p / "Assets").is_dir() and (p / "ProjectSettings").is_dir()

    def inspect(self, project_path: Path) -> ProjectManifest:
        p = Path(project_path).resolve()
        version = None
        pv_file = p / "ProjectSettings" / "ProjectVersion.txt"
        if pv_file.exists():
            try:
                m = re.search(r"m_EditorVersion:\s*([^\r\n]+)", pv_file.read_text(encoding="utf-8"))
                if m:
                    version = m.group(1).strip()
            except Exception:
                pass

        # Locate first scene
        scenes = list((p / "Assets").rglob("*.unity"))
        entry = str(scenes[0].relative_to(p)) if scenes else "Assets/Scenes/SampleScene.unity"

        return ProjectManifest(
            name=p.name,
            root_path=p,
            engine=EngineType.UNITY,
            engine_version=version,
            entry_point=entry,
            config_file="ProjectSettings/ProjectSettings.asset",
        )

    def build(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        exec_tool = ExecuteCommandTool()
        # Check if C# solution exists for fast compile verification
        sln_files = list(p.glob("*.sln"))
        if sln_files:
            return exec_tool.execute(command=f"dotnet build '{sln_files[0].name}'", cwd=str(p))

        return ToolResult(
            tool_name="unity_build",
            success=True,
            output="Unity project detected. Use Unity Editor batchmode for standalone player builds.",
        )

    def test(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        exec_tool = ExecuteCommandTool()
        sln_files = list(p.glob("*.sln"))
        if sln_files:
            return exec_tool.execute(command="dotnet test", cwd=str(p))
        return ToolResult(tool_name="unity_test", success=True, output="Run via Unity Test Framework in Editor.")

    def validate(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        meta_tool = UnityCheckMetaFilesTool()
        return meta_tool.execute(project_path=str(p))

    def get_tools(self) -> list[BaseTool]:
        return [UnityCheckMetaFilesTool(), UnityInspectVersionTool()]
