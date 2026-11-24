"""Supervisor Agent: Master orchestrator coordinating specialized game dev agents."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

SUPERVISOR_SYSTEM_PROMPT = """You are the Lead Game Technical Director and Supervisor Agent.
Your responsibility is to oversee the end-to-end development of game features, coordinate specialized sub-agents, and verify overall architecture.

Your capabilities:
1. Break down high-level game requirements into concrete subtasks.
2. Delegate to Universal Developer, Debugger, Code Reviewer, or QA Agent.
3. Review code changes, build results, and test reports.
4. Ensure engine standards (Phaser, Unity, Unreal, Three.js, Godot) are rigorously adhered to.

Always maintain a high standard of code quality, asset structure, and architecture.
"""


class SupervisorAgent(BaseAgent):
    """Supervisor Agent coordinating multi-agent workflows."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="supervisor",
            role="Lead Game Technical Director & Supervisor",
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            tools=[
                "list_files",
                "read_file",
                "search_files",
                "project_tree",
                "inspect_scene",
                "inspect_objects",
                "inspect_components",
                "git_status",
                "git_diff",
                "search_docs",
            ],
            temperature=0.2,
        )
        super().__init__(config=config, **kwargs)
