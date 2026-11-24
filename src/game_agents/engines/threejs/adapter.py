"""Three.js Engine Adapter."""

import json
from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.engines.base_adapter import BaseEngineAdapter
from game_agents.engines.threejs.tools import (
    ThreejsInspectCanvasTool,
    ThreejsValidateShadersTool,
)
from game_agents.tools.base import BaseTool
from game_agents.tools.terminal.execute_command import ExecuteCommandTool


class ThreejsAdapter(BaseEngineAdapter):
    """Adapter for Three.js 3D Web games."""

    engine_type = EngineType.THREEJS
    name = "threejs"

    def detect(self, project_path: Path) -> bool:
        p = Path(project_path)
        pkg = p / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "three" in deps or "@types/three" in deps:
                    return True
            except Exception:
                pass

        index = p / "index.html"
        if index.exists():
            try:
                text = index.read_text(encoding="utf-8", errors="ignore")
                if "three.js" in text or "three.min.js" in text:
                    return True
            except Exception:
                pass

        return False

    def inspect(self, project_path: Path) -> ProjectManifest:
        p = Path(project_path).resolve()
        pkg = p / "package.json"
        version = None
        name = p.name

        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                name = data.get("name", p.name)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                version = deps.get("three")
            except Exception:
                pass

        return ProjectManifest(
            name=name,
            root_path=p,
            engine=EngineType.THREEJS,
            engine_version=version,
            entry_point="index.html" if (p / "index.html").exists() else "main.js",
            config_file="package.json" if pkg.exists() else None,
        )

    def build(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        pkg = p / "package.json"
        exec_tool = ExecuteCommandTool()

        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                if "build" in data.get("scripts", {}):
                    return exec_tool.execute(command="npm run build", cwd=str(p))
            except Exception:
                pass

        if (p / "index.html").exists():
            return ToolResult(tool_name="threejs_build", success=True, output="Static Three.js page ready to serve.")
        return ToolResult(tool_name="threejs_build", success=False, error="No index.html or build script found.")

    def test(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        exec_tool = ExecuteCommandTool()
        if (p / "package.json").exists():
            return exec_tool.execute(command="npm test", cwd=str(p))
        return ToolResult(tool_name="threejs_test", success=True, output="No test runner configured for Three.js project.")

    def validate(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        if not (p / "index.html").exists():
            return ToolResult(tool_name="threejs_validate", success=False, error="Missing index.html entry point.")
        return ToolResult(tool_name="threejs_validate", success=True, output="Three.js project validation passed.")

    def get_tools(self) -> list[BaseTool]:
        return [ThreejsInspectCanvasTool(), ThreejsValidateShadersTool()]
