"""Planner Agent: Decomposes game features into structured, dependency-aware task graphs."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

PLANNER_SYSTEM_PROMPT = """You are the Game Feature Planner Agent.
Your role is to analyze game requirements and break them down into sequenced, atomic tasks.

Guidelines:
1. Define the prerequisites for each step (e.g. Asset loading -> Scene setup -> Player controller -> Physics setup -> UI HUD).
2. Specify the target engine conventions (Phaser 3 scenes, Unity MonoBehaviours/ScriptableObjects, Three.js meshes, etc.).
3. Mark high-risk or complex tasks as HIGH or CRITICAL priority.
4. Identify which agent role should execute each step (Universal Developer, QA Agent, Debugger).

Produce structured, actionable plans that developers can execute without ambiguity.
"""


class PlannerAgent(BaseAgent):
    """Planner Agent designing structured execution plans."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="planner",
            role="Game Feature Planner & Architect",
            system_prompt=PLANNER_SYSTEM_PROMPT,
            tools=[
                "list_files",
                "read_file",
                "search_files",
                "project_tree",
                "inspect_scene",
                "inspect_assets",
                "search_docs",
            ],
            temperature=0.1,
        )
        super().__init__(config=config, **kwargs)
