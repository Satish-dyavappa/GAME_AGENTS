"""Tool to display project file tree."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class ProjectTreeInput(BaseModel):
    directory: str = Field(default=".", description="Root directory to generate tree from")
    max_depth: int = Field(default=3, description="Maximum recursion depth")


class ProjectTreeTool(BaseTool):
    name: str = "project_tree"
    description: str = "Generate an ASCII directory tree of files and folders in a project."
    args_schema: type[BaseModel] = ProjectTreeInput

    def execute(self, directory: str = ".", max_depth: int = 3) -> ToolResult:
        root = Path(directory).resolve()
        if not root.exists() or not root.is_dir():
            return ToolResult(tool_name=self.name, success=False, error=f"Directory not found: {directory}")

        lines = [root.name + "/"]
        ignored = {".git", ".venv", "__pycache__", "node_modules", ".idea", ".vscode"}

        def _build_tree(curr_dir: Path, prefix: str = "", depth: int = 0) -> None:
            if depth >= max_depth:
                return

            try:
                entries = sorted(
                    [e for e in curr_dir.iterdir() if e.name not in ignored and not e.name.startswith(".")],
                    key=lambda x: (x.is_file(), x.name.lower()),
                )
            except PermissionError:
                return

            total = len(entries)
            for idx, entry in enumerate(entries):
                is_last = idx == total - 1
                connector = "└── " if is_last else "├── "
                next_prefix = prefix + ("    " if is_last else "│   ")

                if entry.is_dir():
                    lines.append(f"{prefix}{connector}{entry.name}/")
                    _build_tree(entry, next_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}{entry.name}")

        _build_tree(root, depth=0)
        return ToolResult(tool_name=self.name, success=True, output="\n".join(lines))
