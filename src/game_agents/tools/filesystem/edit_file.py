"""Tool for precise in-place string replacement in files."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class EditFileInput(BaseModel):
    path: str = Field(..., description="Path of the file to edit")
    target: str = Field(..., description="Exact string to find and replace")
    replacement: str = Field(..., description="Replacement string")


class EditFileTool(BaseTool):
    name: str = "edit_file"
    description: str = "Perform an exact string replacement inside a file."
    args_schema: type[BaseModel] = EditFileInput

    def execute(self, path: str, target: str, replacement: str) -> ToolResult:
        file_path = Path(path).resolve()
        if not file_path.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"File not found: {path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if target not in content:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Target string not found in {path}. Make sure target matches exact characters and whitespace.",
                )

            count = content.count(target)
            new_content = content.replace(target, replacement)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Successfully replaced {count} occurrence(s) in {path}",
                data={"path": str(file_path), "replacements": count},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to edit file {path}: {str(e)}")
