"""Browser automation tools using Playwright for web games and UI testing."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


def _format_target_url(target: str) -> str:
    """Format file path or URL into proper browser navigation target."""
    p = Path(target)
    if p.exists():
        return p.resolve().as_uri()
    if not (target.startswith("http://") or target.startswith("https://") or target.startswith("file://")):
        return f"http://{target}"
    return target


# 1. Screenshot Tool
class BrowserScreenshotInput(BaseModel):
    url_or_path: str = Field(..., description="Web URL or local HTML file path to render")
    output_path: str = Field(default="screenshot.png", description="File path where screenshot will be saved")
    wait_seconds: float = Field(default=2.0, description="Seconds to wait after load for game engine initialization")
    full_page: bool = Field(default=False, description="Whether to capture entire scrollable page")


class BrowserScreenshotTool(BaseTool):
    name: str = "browser_screenshot"
    description: str = "Capture a screenshot of a running web game or HTML page to inspect visuals."
    args_schema: type[BaseModel] = BrowserScreenshotInput

    def execute(
        self,
        url_or_path: str,
        output_path: str = "screenshot.png",
        wait_seconds: float = 2.0,
        full_page: bool = False,
    ) -> ToolResult:
        try:
            from playwright.sync_api import sync_playwright

            target_url = _format_target_url(url_or_path)
            out_file = Path(output_path).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                page.goto(target_url, wait_until="load", timeout=30000)
                page.wait_for_timeout(int(wait_seconds * 1000))
                page.screenshot(path=str(out_file), full_page=full_page)
                browser.close()

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Screenshot saved to {out_file}",
                data={"output_path": str(out_file)},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Screenshot capture failed: {str(e)}")


# 2. Browser Click / Interaction Tool
class BrowserClickInput(BaseModel):
    url_or_path: str = Field(..., description="Web URL or local HTML file path")
    selector: str = Field(..., description="CSS or text selector to click (e.g., 'button#start', '#canvas', 'text=Play')")
    wait_after_seconds: float = Field(default=1.0, description="Seconds to wait after click")


class BrowserClickTool(BaseTool):
    name: str = "browser_click"
    description: str = "Click an element (e.g. start button, canvas, UI button) in a web game."
    args_schema: type[BaseModel] = BrowserClickInput

    def execute(self, url_or_path: str, selector: str, wait_after_seconds: float = 1.0) -> ToolResult:
        try:
            from playwright.sync_api import sync_playwright

            target_url = _format_target_url(url_or_path)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(target_url, wait_until="load", timeout=30000)
                page.wait_for_selector(selector, timeout=10000)
                page.click(selector)
                page.wait_for_timeout(int(wait_after_seconds * 1000))
                page_title = page.title()
                browser.close()

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Successfully clicked selector '{selector}' on {url_or_path}. Page title: {page_title}",
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Click interaction failed: {str(e)}")


# 3. Browser Console Logs Tool
class BrowserConsoleLogsInput(BaseModel):
    url_or_path: str = Field(..., description="Web URL or local HTML file path")
    wait_seconds: float = Field(default=3.0, description="Duration to monitor console logs")


class BrowserConsoleLogsTool(BaseTool):
    name: str = "browser_console_logs"
    description: str = "Inspect browser console messages and JavaScript runtime errors in a game."
    args_schema: type[BaseModel] = BrowserConsoleLogsInput

    def execute(self, url_or_path: str, wait_seconds: float = 3.0) -> ToolResult:
        try:
            from playwright.sync_api import sync_playwright

            target_url = _format_target_url(url_or_path)
            logs: list[dict[str, str]] = []
            page_errors: list[str] = []

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.on("console", lambda msg: logs.append({"type": msg.type, "text": msg.text}))
                page.on("pageerror", lambda err: page_errors.append(str(err)))

                page.goto(target_url, wait_until="load", timeout=30000)
                page.wait_for_timeout(int(wait_seconds * 1000))
                browser.close()

            formatted_logs = [f"[{entry['type'].upper()}] {entry['text']}" for entry in logs]
            if page_errors:
                formatted_logs.append("--- PAGE ERRORS ---")
                formatted_logs.extend([f"[ERROR] {err}" for err in page_errors])

            output_text = "\n".join(formatted_logs) if formatted_logs else "No console messages recorded."
            has_errors = any(entry["type"] == "error" for entry in logs) or len(page_errors) > 0

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=output_text,
                data={"total_logs": len(logs), "has_errors": has_errors, "errors": page_errors},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to inspect console logs: {str(e)}")
