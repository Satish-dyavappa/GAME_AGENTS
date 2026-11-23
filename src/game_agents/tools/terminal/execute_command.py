"""Tool to execute shell commands with security timeouts."""

import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class ExecuteCommandInput(BaseModel):
    command: str = Field(..., description="The shell command string to execute")
    cwd: str | None = Field(default=None, description="Working directory for the command execution")
    timeout_seconds: int = Field(default=60, description="Max execution time in seconds")


class ExecuteCommandTool(BaseTool):
    name: str = "execute_command"
    description: str = "Execute a shell command (e.g. npm, node, python, dotnet, git, cargo) and return stdout/stderr."
    args_schema: type[BaseModel] = ExecuteCommandInput

    def execute(self, command: str, cwd: str | None = None, timeout_seconds: int = 60) -> ToolResult:
        work_dir = Path(cwd).resolve() if cwd else Path.cwd()
        if not work_dir.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Working directory does not exist: {cwd}")

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            success = res.returncode == 0
            stdout = res.stdout.strip()
            stderr = res.stderr.strip()
            output = stdout if stdout else (stderr if not success else "[Command produced no output]")

            return ToolResult(
                tool_name=self.name,
                success=success,
                output=output,
                data={"returncode": res.returncode, "stdout": stdout, "stderr": stderr},
                error=stderr if not success else None,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=f"Command timed out after {timeout_seconds} seconds: {command}",
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Execution error: {str(e)}")
