"""Git tools: status, diff, branch, and commit."""

import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


def _run_git(args: list[str], cwd: Path) -> tuple[bool, str, str]:
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)


# 1. Git Status Tool
class GitStatusInput(BaseModel):
    directory: str = Field(default=".", description="Git repository directory")


class GitStatusTool(BaseTool):
    name: str = "git_status"
    description: str = "Show working tree status: modified, staged, and untracked files."
    args_schema: type[BaseModel] = GitStatusInput

    def execute(self, directory: str = ".") -> ToolResult:
        repo = Path(directory).resolve()
        ok, out, err = _run_git(["status", "--short"], repo)
        if not ok:
            return ToolResult(tool_name=self.name, success=False, error=err or "Git status failed")
        return ToolResult(tool_name=self.name, success=True, output=out if out else "Working tree clean.")


# 2. Git Diff Tool
class GitDiffInput(BaseModel):
    directory: str = Field(default=".", description="Git repository directory")
    path: str | None = Field(default=None, description="Optional specific file or path to diff")
    staged: bool = Field(default=False, description="Whether to view staged changes (--cached)")


class GitDiffTool(BaseTool):
    name: str = "git_diff"
    description: str = "Show changes between commits, commit and working tree, etc."
    args_schema: type[BaseModel] = GitDiffInput

    def execute(self, directory: str = ".", path: str | None = None, staged: bool = False) -> ToolResult:
        repo = Path(directory).resolve()
        args = ["diff"]
        if staged:
            args.append("--cached")
        if path:
            args.extend(["--", path])

        ok, out, err = _run_git(args, repo)
        if not ok:
            return ToolResult(tool_name=self.name, success=False, error=err or "Git diff failed")
        return ToolResult(tool_name=self.name, success=True, output=out if out else "No changes detected.")


# 3. Git Branch Tool
class GitBranchInput(BaseModel):
    directory: str = Field(default=".", description="Git repository directory")
    action: str = Field(default="list", description="Action: 'list', 'create', 'checkout'")
    branch_name: str | None = Field(default=None, description="Branch name for create or checkout")


class GitBranchTool(BaseTool):
    name: str = "git_branch"
    description: str = "List, create, or switch git branches."
    args_schema: type[BaseModel] = GitBranchInput

    def execute(self, directory: str = ".", action: str = "list", branch_name: str | None = None) -> ToolResult:
        repo = Path(directory).resolve()
        if action == "list":
            ok, out, err = _run_git(["branch", "-a"], repo)
        elif action == "create":
            if not branch_name:
                return ToolResult(tool_name=self.name, success=False, error="branch_name required to create branch")
            ok, out, err = _run_git(["checkout", "-b", branch_name], repo)
        elif action == "checkout":
            if not branch_name:
                return ToolResult(tool_name=self.name, success=False, error="branch_name required to checkout branch")
            ok, out, err = _run_git(["checkout", branch_name], repo)
        else:
            return ToolResult(tool_name=self.name, success=False, error=f"Unknown branch action: {action}")

        if not ok:
            return ToolResult(tool_name=self.name, success=False, error=err or f"Git branch {action} failed")
        return ToolResult(tool_name=self.name, success=True, output=out if out else f"Branch {action} completed.")


# 4. Git Commit Tool
class GitCommitInput(BaseModel):
    directory: str = Field(default=".", description="Git repository directory")
    message: str = Field(..., description="Commit message")
    files: list[str] = Field(default_factory=list, description="Files to add, or empty list to stage all modified files (-A)")


class GitCommitTool(BaseTool):
    name: str = "git_commit"
    description: str = "Stage changes and create a git commit."
    args_schema: type[BaseModel] = GitCommitInput

    def execute(self, message: str, directory: str = ".", files: list[str] | None = None) -> ToolResult:
        repo = Path(directory).resolve()
        files = files or []

        # Stage files
        stage_args = ["add"] + (files if files else ["-A"])
        ok, out, err = _run_git(stage_args, repo)
        if not ok:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to stage files: {err}")

        # Commit
        ok, out, err = _run_git(["commit", "-m", message], repo)
        if not ok:
            return ToolResult(tool_name=self.name, success=False, error=f"Commit failed: {err}")
        return ToolResult(tool_name=self.name, success=True, output=out)
