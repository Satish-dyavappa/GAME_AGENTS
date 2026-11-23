"""Tool to search files by glob pattern or keyword."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class SearchFilesInput(BaseModel):
    directory: str = Field(default=".", description="Root directory to search")
    pattern: str = Field(default="*", description="Glob pattern (e.g. '*.js', '*.ts', '*.cs')")
    keyword: str | None = Field(default=None, description="Optional text keyword to find inside file contents")
    max_results: int = Field(default=50, description="Maximum number of matches to return")


class SearchFilesTool(BaseTool):
    name: str = "search_files"
    description: str = "Find files by filename glob pattern or by text content inside files."
    args_schema: type[BaseModel] = SearchFilesInput

    def execute(
        self,
        directory: str = ".",
        pattern: str = "*",
        keyword: str | None = None,
        max_results: int = 50,
    ) -> ToolResult:
        root_dir = Path(directory).resolve()
        if not root_dir.exists() or not root_dir.is_dir():
            return ToolResult(tool_name=self.name, success=False, error=f"Directory not found: {directory}")

        matches: list[str] = []
        try:
            for path in root_dir.rglob(pattern):
                # Skip hidden directories like .git
                if any(part.startswith(".") for part in path.parts):
                    continue

                if path.is_file():
                    if keyword:
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                                if keyword in f.read():
                                    matches.append(str(path.relative_to(root_dir)))
                        except Exception:
                            continue
                    else:
                        matches.append(str(path.relative_to(root_dir)))

                if len(matches) >= max_results:
                    break

            output = "\n".join(matches) if matches else "No matching files found."
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=output,
                data={"total_matches": len(matches), "matches": matches},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Search failed: {str(e)}")
