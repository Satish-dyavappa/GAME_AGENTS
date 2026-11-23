"""Tool to list directory files and folders."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class ListFilesInput(BaseModel):
    directory: str = Field(default=".", description="Path of directory to list")
    include_hidden: bool = Field(default=False, description="Whether to include hidden files (starting with .)")


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "List all files and subdirectories inside a given directory."
    args_schema: type[BaseModel] = ListFilesInput

    def execute(self, directory: str = ".", include_hidden: bool = False) -> ToolResult:
        dir_path = Path(directory).resolve()
        if not dir_path.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Directory not found: {directory}")
        if not dir_path.is_dir():
            return ToolResult(tool_name=self.name, success=False, error=f"Path is not a directory: {directory}")

        try:
            items = []
            for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if not include_hidden and item.name.startswith("."):
                    continue
                type_indicator = "[DIR]" if item.is_dir() else "[FILE]"
                size_str = f"({item.stat().st_size} bytes)" if item.is_file() else ""
                items.append(f"{type_indicator:<6} {item.name} {size_str}".strip())

            output = "\n".join(items) if items else "[Empty directory]"
            return ToolResult(tool_name=self.name, success=True, output=output, data={"count": len(items)})
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to list directory: {str(e)}")
