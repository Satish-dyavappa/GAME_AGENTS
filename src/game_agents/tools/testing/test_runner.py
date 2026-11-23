"""Automated test runners for game unit and integration tests."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool
from game_agents.tools.terminal.execute_command import ExecuteCommandTool


# 1. Run Unit Tests Tool
class RunUnitTestsInput(BaseModel):
    directory: str = Field(default=".", description="Project root directory")
    framework: str | None = Field(default=None, description="Test runner: 'npm', 'jest', 'vitest', 'pytest', 'dotnet'")
    test_path: str | None = Field(default=None, description="Optional specific test file to run")


class RunUnitTestsTool(BaseTool):
    name: str = "run_unit_tests"
    description: str = "Run unit test suite (Jest, Vitest, Pytest, dotnet test) to verify game logic."
    args_schema: type[BaseModel] = RunUnitTestsInput

    def execute(self, directory: str = ".", framework: str | None = None, test_path: str | None = None) -> ToolResult:
        dir_path = Path(directory).resolve()
        fw = framework

        # Auto-detect framework
        if not fw:
            if (dir_path / "package.json").exists():
                fw = "npm"
            elif (dir_path / "pyproject.toml").exists() or (dir_path / "pytest.ini").exists():
                fw = "pytest"
            else:
                fw = "npm"

        if fw == "npm":
            cmd = f"npm test -- {test_path}" if test_path else "npm test"
        elif fw in ("jest", "vitest"):
            cmd = f"npx {fw} run {test_path or ''}"
        elif fw == "pytest":
            cmd = f"pytest {test_path or ''}"
        elif fw == "dotnet":
            cmd = "dotnet test"
        else:
            cmd = f"{fw} {test_path or ''}"

        exec_tool = ExecuteCommandTool()
        res = exec_tool.execute(command=cmd, cwd=str(dir_path), timeout_seconds=120)
        return ToolResult(
            tool_name=self.name,
            success=res.success,
            output=res.output,
            error=res.error,
            data=res.data,
        )


# 2. Run Integration Tests Tool
class RunIntegrationTestsInput(BaseModel):
    directory: str = Field(default=".", description="Project root directory")
    command: str | None = Field(default=None, description="Specific integration test command, or auto-detect")


class RunIntegrationTestsTool(BaseTool):
    name: str = "run_integration_tests"
    description: str = "Execute end-to-end or gameplay integration test suites."
    args_schema: type[BaseModel] = RunIntegrationTestsInput

    def execute(self, directory: str = ".", command: str | None = None) -> ToolResult:
        dir_path = Path(directory).resolve()
        cmd = command or "npm run test:e2e"

        exec_tool = ExecuteCommandTool()
        res = exec_tool.execute(command=cmd, cwd=str(dir_path), timeout_seconds=180)
        return ToolResult(
            tool_name=self.name,
            success=res.success,
            output=res.output,
            error=res.error,
            data=res.data,
        )
