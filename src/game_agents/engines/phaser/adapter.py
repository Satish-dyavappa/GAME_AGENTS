"""Phaser Engine Adapter."""

import json
from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType, ProjectManifest
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.engines.base_adapter import BaseEngineAdapter
from game_agents.engines.phaser.tools import (
    PhaserCreateSceneTool,
    PhaserInspectConfigTool,
)
from game_agents.tools.base import BaseTool
from game_agents.tools.terminal.execute_command import ExecuteCommandTool


class PhaserAdapter(BaseEngineAdapter):
    """Adapter for Phaser 3 web games."""

    engine_type = EngineType.PHASER
    name = "phaser"

    def detect(self, project_path: Path) -> bool:
        p = Path(project_path)
        pkg = p / "package.json"
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "phaser" in deps:
                    return True
            except Exception:
                pass

        # Also detect via index.html script tag
        index_html = Path(project_path) / "index.html"
        if index_html.exists():
            try:
                text = index_html.read_text(encoding="utf-8", errors="ignore")
                if "phaser" in text.lower():
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
                version = deps.get("phaser")
            except Exception:
                pass

        entry = "index.html" if (p / "index.html").exists() else "main.js"

        return ProjectManifest(
            name=name,
            root_path=p,
            engine=EngineType.PHASER,
            engine_version=version,
            entry_point=entry,
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

        # Static Phaser game check
        if (p / "index.html").exists():
            return ToolResult(
                tool_name="phaser_build",
                success=True,
                output="Static Phaser game detected. Ready to serve (no compilation required).",
            )
        return ToolResult(tool_name="phaser_build", success=False, error="No index.html or build script found.")

    def test(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        exec_tool = ExecuteCommandTool()
        if (p / "package.json").exists():
            return exec_tool.execute(command="npm test", cwd=str(p))
        return ToolResult(tool_name="phaser_test", success=True, output="No test suite configured for this Phaser project.")

    def validate(self, project_path: Path) -> ToolResult:
        p = Path(project_path).resolve()
        issues = []

        if not (p / "index.html").exists():
            issues.append("Missing index.html entry point.")

        has_js = any(p.rglob("*.js")) or any(p.rglob("*.ts"))
        if not has_js:
            issues.append("No JavaScript or TypeScript game scripts found.")

        if issues:
            return ToolResult(tool_name="phaser_validate", success=False, error="\n".join(issues))
        return ToolResult(tool_name="phaser_validate", success=True, output="Phaser project validation passed.")

    def get_tools(self) -> list[BaseTool]:
        return [PhaserCreateSceneTool(), PhaserInspectConfigTool()]
