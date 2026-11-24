"""Project Analyzer Agent: Scans repositories, identifies engine, scenes, assets, and project manifests."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

PROJECT_ANALYZER_SYSTEM_PROMPT = """You are the Game Project Analyzer Agent.
Your job is to inspect an unfamiliar or existing game repository and produce an exhaustive architectural breakdown.

Analyze:
1. Target Game Engine (Phaser, Unity, Unreal, Three.js, Godot, Custom Web Canvas).
2. Entry point, main scenes, and boot scripts.
3. Asset inventory (spritesheets, models, audio, textures).
4. Dependencies and package manager (package.json, Cargo.toml, requirements.txt).
5. Architecture patterns used (ECS, State Machines, Component-based, Monolithic).

Provide a clear, structured summary with actionable insights for developers.
"""


class ProjectAnalyzerAgent(BaseAgent):
    """Project Analyzer Agent analyzing codebase structure."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="project_analyzer",
            role="Game Project Architecture Analyzer",
            system_prompt=PROJECT_ANALYZER_SYSTEM_PROMPT,
            tools=[
                "list_files",
                "read_file",
                "search_files",
                "project_tree",
                "inspect_scene",
                "inspect_objects",
                "inspect_components",
                "inspect_assets",
                "inspect_spritesheet",
                "inspect_audio",
            ],
            temperature=0.1,
        )
        super().__init__(config=config, **kwargs)
