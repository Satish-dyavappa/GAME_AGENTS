"""Code Reviewer Agent: Audits game code for performance, architecture, and engine best practices."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

CODE_REVIEWER_SYSTEM_PROMPT = """You are the Game Code Reviewer Agent.
Your responsibility is to review pull requests and game code changes for performance, engine standards, and maintainability.

Review Criteria:
1. Performance: GC allocations inside update() loops, unbatched draw calls, texture memory leaks.
2. Robustness: Null safety, edge-case bounds checking, player out-of-bounds handling.
3. Architecture: Clean separation of concerns (Input -> Controller -> Game State -> View/Renderer).
4. Git changes: Inspect `git_diff` to review modifications.

Provide clear, prioritized review comments (CRITICAL, WARNING, SUGGESTION) with code snippets.
"""


class CodeReviewerAgent(BaseAgent):
    """Code Reviewer Agent inspecting game code quality."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="code_reviewer",
            role="Game Code Quality & Performance Reviewer",
            system_prompt=CODE_REVIEWER_SYSTEM_PROMPT,
            tools=[
                "read_file",
                "search_files",
                "git_diff",
                "git_status",
                "inspect_components",
                "search_docs",
            ],
            temperature=0.1,
        )
        super().__init__(config=config, **kwargs)
