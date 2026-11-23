"""Assets inspection tools: images, audio, spritesheets, models."""

import json
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg"}
AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav", ".aac", ".flac"}
SPRITESHEET_JSON_EXTENSIONS = {".json"}
MODEL_EXTENSIONS = {".gltf", ".glb", ".fbx", ".obj"}


# 1. Inspect Assets Tool
class InspectAssetsInput(BaseModel):
    assets_dir: str = Field(default="assets", description="Directory to scan for game assets")
    asset_type: str | None = Field(default=None, description="Optional filter: 'images', 'audio', 'models', 'all'")


class InspectAssetsTool(BaseTool):
    name: str = "inspect_assets"
    description: str = "Scan game assets directory and report image, audio, model, and spritesheet files with sizes."
    args_schema: type[BaseModel] = InspectAssetsInput

    def execute(self, assets_dir: str = "assets", asset_type: str | None = None) -> ToolResult:
        root = Path(assets_dir).resolve()
        if not root.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Assets directory not found: {assets_dir}")

        categorized: dict[str, list[dict[str, str | int]]] = {
            "images": [],
            "audio": [],
            "models": [],
            "other": [],
        }

        for path in root.rglob("*.*"):
            if any(p.startswith(".") for p in path.parts):
                continue
            ext = path.suffix.lower()
            size = path.stat().st_size
            item = {"name": path.name, "path": str(path.relative_to(root)), "size_bytes": size}

            if ext in IMAGE_EXTENSIONS:
                categorized["images"].append(item)
            elif ext in AUDIO_EXTENSIONS:
                categorized["audio"].append(item)
            elif ext in MODEL_EXTENSIONS:
                categorized["models"].append(item)
            else:
                categorized["other"].append(item)

        report = []
        for cat, items in categorized.items():
            if asset_type and asset_type.lower() != "all" and cat != asset_type.lower():
                continue
            report.append(f"### {cat.upper()} ({len(items)} files):")
            for i in items[:20]:  # Cap at 20 per category for readable prompt context
                report.append(f"  - {i['name']} ({i['size_bytes']} bytes)")
            if len(items) > 20:
                report.append(f"  ... and {len(items) - 20} more")

        return ToolResult(
            tool_name=self.name,
            success=True,
            output="\n".join(report) if report else "No matching assets found.",
            data=categorized,
        )


# 2. Inspect Spritesheet Tool
class InspectSpritesheetInput(BaseModel):
    path: str = Field(..., description="Path to spritesheet image (.png) or spritesheet atlas metadata (.json)")


class InspectSpritesheetTool(BaseTool):
    name: str = "inspect_spritesheet"
    description: str = "Inspect spritesheet configuration, frame dimensions, and animation sequences."
    args_schema: type[BaseModel] = InspectSpritesheetInput

    def execute(self, path: str) -> ToolResult:
        target = Path(path).resolve()
        if not target.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Spritesheet path not found: {path}")

        if target.suffix.lower() == ".json":
            try:
                data = json.loads(target.read_text(encoding="utf-8"))
                frames = data.get("frames", {})
                meta = data.get("meta", {})
                num_frames = len(frames) if isinstance(frames, (list, dict)) else 0
                frame_names = list(frames.keys())[:10] if isinstance(frames, dict) else []

                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output=f"Spritesheet Atlas: {target.name}\nTotal frames: {num_frames}\nImage: {meta.get('image', 'unknown')}\nSample frames: {frame_names}",
                    data={"frames_count": num_frames, "meta": meta},
                )
            except Exception as e:
                return ToolResult(tool_name=self.name, success=False, error=f"Failed to parse spritesheet JSON: {str(e)}")

        # If it's an image file
        size = target.stat().st_size
        return ToolResult(
            tool_name=self.name,
            success=True,
            output=f"Spritesheet Image: {target.name} (File size: {size} bytes)",
            data={"path": str(target), "size_bytes": size},
        )


# 3. Inspect Audio Tool
class InspectAudioInput(BaseModel):
    path: str = Field(..., description="Path to audio file (.mp3, .ogg, .wav)")


class InspectAudioTool(BaseTool):
    name: str = "inspect_audio"
    description: str = "Inspect game audio file format, size, and validity."
    args_schema: type[BaseModel] = InspectAudioInput

    def execute(self, path: str) -> ToolResult:
        target = Path(path).resolve()
        if not target.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Audio file not found: {path}")

        ext = target.suffix.lower()
        if ext not in AUDIO_EXTENSIONS:
            return ToolResult(tool_name=self.name, success=False, error=f"File {path} is not a recognized audio format ({AUDIO_EXTENSIONS})")

        size_kb = round(target.stat().st_size / 1024, 2)
        return ToolResult(
            tool_name=self.name,
            success=True,
            output=f"Audio File: {target.name}\nFormat: {ext}\nSize: {size_kb} KB",
            data={"filename": target.name, "format": ext, "size_kb": size_kb},
        )
