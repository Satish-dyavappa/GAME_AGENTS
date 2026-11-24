"""Central registry for discovering and routing game engine adapters."""

from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType
from game_agents.engines.base_adapter import BaseEngineAdapter


class EngineRegistry:
    """Registry managing game engine adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, BaseEngineAdapter] = {}

    def register(self, adapter: BaseEngineAdapter) -> None:
        """Register an engine adapter instance."""
        self._adapters[adapter.engine_type.value] = adapter
        self._adapters[adapter.name.lower()] = adapter

    def get(self, engine_key: str | EngineType) -> BaseEngineAdapter | None:
        """Retrieve an adapter by engine name or EngineType."""
        key = engine_key.value if isinstance(engine_key, EngineType) else engine_key.lower()
        return self._adapters.get(key)

    def detect(self, project_path: str | Path) -> BaseEngineAdapter | None:
        """Scan a directory and automatically return the matching engine adapter."""
        path = Path(project_path).resolve()
        if not path.exists():
            return None

        # Check each unique registered adapter
        checked: set[str] = set()
        for adapter in self._adapters.values():
            if adapter.name in checked:
                continue
            checked.add(adapter.name)
            if adapter.detect(path):
                return adapter

        return None

    def get_all(self) -> list[BaseEngineAdapter]:
        """Return all distinct registered adapters."""
        seen: set[str] = set()
        unique = []
        for a in self._adapters.values():
            if a.name not in seen:
                seen.add(a.name)
                unique.append(a)
        return unique


# Global default engine registry
default_engine_registry = EngineRegistry()
