"""Tool to create or overwrite files."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class WriteFileInput(BaseModel):
    path: str = Field(..., description="Path where file should be created or written")
    content: str = Field(..., description="Full text content to write into the file")
    overwrite: bool = Field(default=True, description="Whether to overwrite existing file")


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Create a new file or overwrite an existing file with the provided content."
    args_schema: type[BaseModel] = WriteFileInput

    def execute(self, path: str, content: str, overwrite: bool = True) -> ToolResult:
        file_path = Path(path).resolve()

        if file_path.exists() and not overwrite:
            return ToolResult(tool_name=self.name, success=False, error=f"File already exists and overwrite is False: {path}")

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Successfully wrote {len(content)} characters to {path}",
                data={"path": str(file_path), "bytes_written": len(content.encode("utf-8"))},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to write file {path}: {str(e)}")
