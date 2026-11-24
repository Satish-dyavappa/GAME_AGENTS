"""Universal Developer Agent: Implements game mechanics, scenes, shaders, and controllers."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

DEVELOPER_SYSTEM_PROMPT = """You are the Universal Game Developer Agent.
You write production-quality game code across Phaser (JS/TS), Unity (C#), Three.js (JS/GLSL), Unreal (C++/Blueprints), and Godot (GDScript).

Coding Principles:
1. Clean, modular, well-commented game logic.
2. Proper lifecycle adherence (preload, create, update, destroy).
3. Frame-rate independent delta timing (use delta time for movement and physics).
4. Asset and memory management (destroy unneeded sprites/textures, clean up event listeners).
5. Accurate engine syntax (e.g., Arcade Physics in Phaser, CharacterController in Unity).

Use filesystem tools (`write_file`, `edit_file`, `read_file`) to apply your implementations directly.
"""


class DeveloperAgent(BaseAgent):
    """Universal Developer Agent writing game code and mechanics."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="developer",
            role="Universal Game Developer",
            system_prompt=DEVELOPER_SYSTEM_PROMPT,
            tools=[
                "read_file",
                "write_file",
                "edit_file",
                "list_files",
                "search_files",
                "install_dependencies",
                "execute_command",
                "inspect_scene",
                "inspect_objects",
                "inspect_components",
                "inspect_assets",
                "search_docs",
            ],
            temperature=0.2,
        )
        super().__init__(config=config, **kwargs)
