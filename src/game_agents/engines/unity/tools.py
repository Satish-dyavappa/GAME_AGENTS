"""Unity-specific agent tools."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class UnityCheckMetaFilesInput(BaseModel):
    project_path: str = Field(default=".", description="Path to Unity project root")


class UnityCheckMetaFilesTool(BaseTool):
    name: str = "unity_check_meta_files"
    description: str = "Check for missing .meta files in Unity's Assets/ directory to prevent broken GUID references."
    args_schema: type[BaseModel] = UnityCheckMetaFilesInput

    def execute(self, project_path: str = ".") -> ToolResult:
        assets_dir = Path(project_path).resolve() / "Assets"
        if not assets_dir.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Assets directory not found in {project_path}")

        missing_meta = []
        for item in assets_dir.rglob("*"):
            if item.suffix == ".meta":
                continue
            meta_file = item.parent / f"{item.name}.meta"
            if not meta_file.exists():
                missing_meta.append(str(item.relative_to(assets_dir)))

        if missing_meta:
            lines = [f"- {m}" for m in missing_meta[:25]]
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Found {len(missing_meta)} files/folders without corresponding .meta files:\n" + "\n".join(lines),
                data={"missing_count": len(missing_meta), "missing": missing_meta},
            )

        return ToolResult(
            tool_name=self.name,
            success=True,
            output="All assets have valid corresponding .meta files.",
        )


class UnityInspectVersionInput(BaseModel):
    project_path: str = Field(default=".", description="Path to Unity project root")


class UnityInspectVersionTool(BaseTool):
    name: str = "unity_inspect_version"
    description: str = "Read the exact Unity editor version and changeset from ProjectVersion.txt."
    args_schema: type[BaseModel] = UnityInspectVersionInput

    def execute(self, project_path: str = ".") -> ToolResult:
        p_file = Path(project_path).resolve() / "ProjectSettings" / "ProjectVersion.txt"
        if not p_file.exists():
            return ToolResult(tool_name=self.name, success=False, error="ProjectSettings/ProjectVersion.txt not found.")

        try:
            content = p_file.read_text(encoding="utf-8")
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Unity Version:\n{content.strip()}",
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to read ProjectVersion.txt: {str(e)}")
