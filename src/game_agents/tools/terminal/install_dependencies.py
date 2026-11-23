"""Tool to install game dependencies across npm, pip, dotnet, cargo."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool
from game_agents.tools.terminal.execute_command import ExecuteCommandTool


class InstallDependenciesInput(BaseModel):
    package_manager: str | None = Field(
        default=None,
        description="Package manager to use: npm, yarn, pnpm, pip, uv, cargo, nuget (or auto-detect if None)",
    )
    packages: list[str] = Field(default_factory=list, description="Specific packages to install, or empty to install all from lockfile/manifest")
    directory: str = Field(default=".", description="Project directory containing manifest")


class InstallDependenciesTool(BaseTool):
    name: str = "install_dependencies"
    description: str = "Install project dependencies using the appropriate package manager (npm, yarn, pip, uv, etc.)."
    args_schema: type[BaseModel] = InstallDependenciesInput

    def execute(
        self,
        package_manager: str | None = None,
        packages: list[str] | None = None,
        directory: str = ".",
    ) -> ToolResult:
        dir_path = Path(directory).resolve()
        packages = packages or []

        pm = package_manager
        if not pm:
            if (dir_path / "package.json").exists():
                pm = "npm"
            elif (dir_path / "pyproject.toml").exists() or (dir_path / "requirements.txt").exists():
                pm = "pip"
            elif (dir_path / "Cargo.toml").exists():
                pm = "cargo"
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Could not auto-detect package manager in {directory}. Please specify package_manager.",
                )

        if pm == "npm":
            cmd = f"npm install {' '.join(packages)}" if packages else "npm install"
        elif pm == "yarn":
            cmd = f"yarn add {' '.join(packages)}" if packages else "yarn install"
        elif pm == "pnpm":
            cmd = f"pnpm add {' '.join(packages)}" if packages else "pnpm install"
        elif pm in ("pip", "uv"):
            installer = "uv pip install" if pm == "uv" else "pip install"
            if packages:
                cmd = f"{installer} {' '.join(packages)}"
            elif (dir_path / "requirements.txt").exists():
                cmd = f"{installer} -r requirements.txt"
            else:
                cmd = f"{installer} -e ."
        elif pm == "cargo":
            cmd = f"cargo add {' '.join(packages)}" if packages else "cargo build"
        else:
            cmd = f"{pm} install {' '.join(packages)}"

        exec_tool = ExecuteCommandTool()
        return exec_tool.execute(command=cmd, cwd=str(dir_path), timeout_seconds=180)
