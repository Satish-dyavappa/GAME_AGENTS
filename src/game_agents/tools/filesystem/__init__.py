"""Filesystem tools package."""

from game_agents.tools.filesystem.edit_file import EditFileInput, EditFileTool
from game_agents.tools.filesystem.list_files import ListFilesInput, ListFilesTool
from game_agents.tools.filesystem.project_tree import ProjectTreeInput, ProjectTreeTool
from game_agents.tools.filesystem.read_file import ReadFileInput, ReadFileTool
from game_agents.tools.filesystem.search_files import SearchFilesInput, SearchFilesTool
from game_agents.tools.filesystem.write_file import WriteFileInput, WriteFileTool
from game_agents.tools.registry import ToolRegistry


def register_filesystem_tools(registry: ToolRegistry) -> None:
    """Register all filesystem tools with the given registry."""
    registry.register(ReadFileTool(), category="filesystem")
    registry.register(WriteFileTool(), category="filesystem")
    registry.register(EditFileTool(), category="filesystem")
    registry.register(SearchFilesTool(), category="filesystem")
    registry.register(ListFilesTool(), category="filesystem")
    registry.register(ProjectTreeTool(), category="filesystem")


__all__ = [
    "ReadFileTool",
    "ReadFileInput",
    "WriteFileTool",
    "WriteFileInput",
    "EditFileTool",
    "EditFileInput",
    "SearchFilesTool",
    "SearchFilesInput",
    "ListFilesTool",
    "ListFilesInput",
    "ProjectTreeTool",
    "ProjectTreeInput",
    "register_filesystem_tools",
]
