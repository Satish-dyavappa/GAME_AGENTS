"""Tool to read file contents."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class ReadFileInput(BaseModel):
    path: str = Field(..., description="Absolute or relative path of the file to read")
    start_line: int | None = Field(default=None, description="Starting line number (1-indexed, inclusive)")
    end_line: int | None = Field(default=None, description="Ending line number (inclusive)")


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read the contents of a file with line numbers or a specific line range."
    args_schema: type[BaseModel] = ReadFileInput

    def execute(self, path: str, start_line: int | None = None, end_line: int | None = None) -> ToolResult:
        file_path = Path(path).resolve()
        if not file_path.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"File not found: {path}")
        if not file_path.is_file():
            return ToolResult(tool_name=self.name, success=False, error=f"Path is not a regular file: {path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            s_idx = max(1, start_line) if start_line is not None else 1
            e_idx = min(total_lines, end_line) if end_line is not None else total_lines

            selected_lines = lines[s_idx - 1 : e_idx]
            numbered = [f"{s_idx + i}: {line}" for i, line in enumerate(selected_lines)]
            content = "".join(numbered)

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=content if content else "[Empty file]",
                data={"total_lines": total_lines, "returned_lines": len(selected_lines)},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to read file {path}: {str(e)}")
