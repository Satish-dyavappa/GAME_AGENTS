"""Browser automation tools module."""

from game_agents.tools.browser.browser_tools import (
    BrowserClickInput,
    BrowserClickTool,
    BrowserConsoleLogsInput,
    BrowserConsoleLogsTool,
    BrowserScreenshotInput,
    BrowserScreenshotTool,
)

__all__ = [
    "BrowserScreenshotTool",
    "BrowserScreenshotInput",
    "BrowserClickTool",
    "BrowserClickInput",
    "BrowserConsoleLogsTool",
    "BrowserConsoleLogsInput",
]
