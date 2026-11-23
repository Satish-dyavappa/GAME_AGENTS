"""Central tools package for game dev agents."""

from game_agents.tools.assets import (
    InspectAssetsTool,
    InspectAudioTool,
    InspectSpritesheetTool,
)
from game_agents.tools.base import BaseTool
from game_agents.tools.browser import (
    BrowserClickTool,
    BrowserConsoleLogsTool,
    BrowserScreenshotTool,
)
from game_agents.tools.docs import SearchDocsTool
from game_agents.tools.engine import (
    InspectComponentsTool,
    InspectObjectsTool,
    InspectSceneTool,
)
from game_agents.tools.filesystem import (
    EditFileTool,
    ListFilesTool,
    ProjectTreeTool,
    ReadFileTool,
    SearchFilesTool,
    WriteFileTool,
    register_filesystem_tools,
)
from game_agents.tools.git import (
    GitBranchTool,
    GitCommitTool,
    GitDiffTool,
    GitStatusTool,
)
from game_agents.tools.registry import ToolRegistry, default_tool_registry
from game_agents.tools.terminal import (
    ExecuteCommandTool,
    InstallDependenciesTool,
)
from game_agents.tools.testing import (
    RunIntegrationTestsTool,
    RunUnitTestsTool,
)


def register_all_tools(registry: ToolRegistry) -> None:
    """Register all 8 tool groups into the central registry."""
    # 1. Filesystem
    register_filesystem_tools(registry)

    # 2. Terminal
    registry.register(ExecuteCommandTool(), category="terminal")
    registry.register(InstallDependenciesTool(), category="terminal")

    # 3. Git
    registry.register(GitStatusTool(), category="git")
    registry.register(GitDiffTool(), category="git")
    registry.register(GitBranchTool(), category="git")
    registry.register(GitCommitTool(), category="git")

    # 4. Browser
    registry.register(BrowserScreenshotTool(), category="browser")
    registry.register(BrowserClickTool(), category="browser")
    registry.register(BrowserConsoleLogsTool(), category="browser")

    # 5. Engine
    registry.register(InspectSceneTool(), category="engine")
    registry.register(InspectObjectsTool(), category="engine")
    registry.register(InspectComponentsTool(), category="engine")

    # 6. Testing
    registry.register(RunUnitTestsTool(), category="testing")
    registry.register(RunIntegrationTestsTool(), category="testing")

    # 7. Assets
    registry.register(InspectAssetsTool(), category="assets")
    registry.register(InspectSpritesheetTool(), category="assets")
    registry.register(InspectAudioTool(), category="assets")

    # 8. Documentation
    registry.register(SearchDocsTool(), category="docs")


# Auto-register all tools into global singleton
register_all_tools(default_tool_registry)

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "default_tool_registry",
    "register_all_tools",
    # Filesystem
    "ReadFileTool",
    "WriteFileTool",
    "EditFileTool",
    "SearchFilesTool",
    "ListFilesTool",
    "ProjectTreeTool",
    # Terminal
    "ExecuteCommandTool",
    "InstallDependenciesTool",
    # Git
    "GitStatusTool",
    "GitDiffTool",
    "GitBranchTool",
    "GitCommitTool",
    # Browser
    "BrowserScreenshotTool",
    "BrowserClickTool",
    "BrowserConsoleLogsTool",
    # Engine
    "InspectSceneTool",
    "InspectObjectsTool",
    "InspectComponentsTool",
    # Testing
    "RunUnitTestsTool",
    "RunIntegrationTestsTool",
    # Assets
    "InspectAssetsTool",
    "InspectSpritesheetTool",
    "InspectAudioTool",
    # Docs
    "SearchDocsTool",
]
