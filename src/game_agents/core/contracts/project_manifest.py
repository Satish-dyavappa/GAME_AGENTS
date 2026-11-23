"""Project manifest contract defining game project metadata."""

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field


class EngineType(StrEnum):
    """Supported game engines and frameworks."""

    PHASER = "phaser"
    UNITY = "unity"
    UNREAL = "unreal"
    GODOT = "godot"
    THREEJS = "threejs"
    WEB = "web"
    CUSTOM = "custom"


class ProjectManifest(BaseModel):
    """Metadata describing a target game project."""

    name: str = Field(..., description="Project name")
    root_path: Path = Field(..., description="Absolute path to game project root")
    engine: EngineType = Field(..., description="Target game engine")
    engine_version: str | None = Field(default=None, description="Engine version if detected")
    entry_point: str | None = Field(default=None, description="Main scene or entry script")
    config_file: str | None = Field(default=None, description="Engine-specific project config")
