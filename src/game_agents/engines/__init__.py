"""Game engine adapters package."""

from game_agents.engines.base_adapter import BaseEngineAdapter
from game_agents.engines.phaser import (
    PhaserAdapter,
    PhaserCreateSceneTool,
    PhaserInspectConfigTool,
)
from game_agents.engines.registry import EngineRegistry, default_engine_registry
from game_agents.engines.threejs import (
    ThreejsAdapter,
    ThreejsInspectCanvasTool,
    ThreejsValidateShadersTool,
)
from game_agents.engines.unity import (
    UnityAdapter,
    UnityCheckMetaFilesTool,
    UnityInspectVersionTool,
)
from game_agents.engines.unreal import (
    UnrealAdapter,
    UnrealInspectUprojectTool,
    UnrealListPluginsTool,
)
from game_agents.tools.registry import default_tool_registry


def register_all_adapters(registry: EngineRegistry) -> None:
    """Register all core game engine adapters."""
    phaser = PhaserAdapter()
    unity = UnityAdapter()
    unreal = UnrealAdapter()
    threejs = ThreejsAdapter()

    registry.register(phaser)
    registry.register(unity)
    registry.register(unreal)
    registry.register(threejs)

    # Automatically register engine tools into global tool registry
    for adapter in (phaser, unity, unreal, threejs):
        for tool in adapter.get_tools():
            default_tool_registry.register(tool, category="engine")


# Auto-register standard engine adapters into global registry
register_all_adapters(default_engine_registry)

__all__ = [
    "BaseEngineAdapter",
    "EngineRegistry",
    "default_engine_registry",
    "register_all_adapters",
    # Adapters
    "PhaserAdapter",
    "UnityAdapter",
    "UnrealAdapter",
    "ThreejsAdapter",
    # Tools
    "PhaserCreateSceneTool",
    "PhaserInspectConfigTool",
    "UnityCheckMetaFilesTool",
    "UnityInspectVersionTool",
    "UnrealInspectUprojectTool",
    "UnrealListPluginsTool",
    "ThreejsInspectCanvasTool",
    "ThreejsValidateShadersTool",
]
