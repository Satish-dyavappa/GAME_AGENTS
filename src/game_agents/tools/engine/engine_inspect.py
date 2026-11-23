"""Engine inspection tools: inspect scenes, objects, and components."""

import json
import re
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


# 1. Inspect Scene Tool
class InspectSceneInput(BaseModel):
    project_path: str = Field(default=".", description="Path to the game project root")
    scene_name: str | None = Field(default=None, description="Optional specific scene name or file to inspect")


class InspectSceneTool(BaseTool):
    name: str = "inspect_scene"
    description: str = "Discover and inspect game scenes in Phaser, Unity, Godot, Unreal, or Web games."
    args_schema: type[BaseModel] = InspectSceneInput

    def execute(self, project_path: str = ".", scene_name: str | None = None) -> ToolResult:
        root = Path(project_path).resolve()
        if not root.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Path not found: {project_path}")

        scenes: list[dict[str, str]] = []

        # 1. Search Phaser / Web scenes (classes extending Phaser.Scene or Scene)
        for js_file in root.rglob("*.js"):
            if any(p.startswith(".") or p == "node_modules" for p in js_file.parts):
                continue
            try:
                content = js_file.read_text(encoding="utf-8", errors="ignore")
                matches = re.findall(r"class\s+([A-Za-z0-9_]+)\s+extends\s+(?:Phaser\.)?Scene", content)
                for m in matches:
                    if not scene_name or scene_name.lower() in m.lower():
                        scenes.append({"engine": "Phaser/Web", "scene": m, "file": str(js_file.relative_to(root))})
            except Exception:
                continue

        # 2. Search Godot scenes (.tscn)
        for tscn in root.rglob("*.tscn"):
            if not scene_name or scene_name.lower() in tscn.stem.lower():
                scenes.append({"engine": "Godot", "scene": tscn.name, "file": str(tscn.relative_to(root))})

        # 3. Search Unity scenes (.unity)
        for unity_scene in root.rglob("*.unity"):
            if not scene_name or scene_name.lower() in unity_scene.stem.lower():
                scenes.append({"engine": "Unity", "scene": unity_scene.name, "file": str(unity_scene.relative_to(root))})

        # 4. Search Unreal maps (.umap)
        for umap in root.rglob("*.umap"):
            if not scene_name or scene_name.lower() in umap.stem.lower():
                scenes.append({"engine": "Unreal", "scene": umap.name, "file": str(umap.relative_to(root))})

        if not scenes:
            return ToolResult(
                tool_name=self.name,
                success=True,
                output="No scenes found matching the criteria.",
                data={"scenes": []},
            )

        output_lines = [f"- [{s['engine']}] {s['scene']} ({s['file']})" for s in scenes]
        return ToolResult(
            tool_name=self.name,
            success=True,
            output="\n".join(output_lines),
            data={"scenes": scenes, "count": len(scenes)},
        )


# 2. Inspect Objects Tool
class InspectObjectsInput(BaseModel):
    file_or_dir: str = Field(default=".", description="File or directory to inspect for game objects / entities")


class InspectObjectsTool(BaseTool):
    name: str = "inspect_objects"
    description: str = "Inspect game objects, sprites, prefabs, or actor entities defined in game scripts."
    args_schema: type[BaseModel] = InspectObjectsInput

    def execute(self, file_or_dir: str = ".") -> ToolResult:
        target = Path(file_or_dir).resolve()
        if not target.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Path not found: {file_or_dir}")

        objects_found: list[dict[str, str]] = []
        files = [target] if target.is_file() else list(target.rglob("*.*"))

        for file in files:
            if any(p.startswith(".") or p in ("node_modules", "dist", "build") for p in file.parts):
                continue
            if file.suffix in (".js", ".ts", ".cs", ".gd", ".cpp", ".h"):
                try:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                    # Match instantiated game objects, sprites, prefabs, physics bodies
                    patterns = [
                        (r"this\.physics\.add\.(?:sprite|image|group)\s*\([^,]+,[^,]+,\s*['\"]([^'\"]+)['\"]", "Phaser Sprite/Image"),
                        (r"this\.add\.(?:sprite|image|text|circle)\s*\([^,]+,[^,]+,\s*['\"]([^'\"]+)['\"]", "Phaser Object"),
                        (r"Instantiate\s*\(\s*([A-Za-z0-9_]+)", "Unity Instantiate"),
                        (r"SpawnActor<([A-Za-z0-9_]+)>", "Unreal SpawnActor"),
                    ]
                    for pat, obj_type in patterns:
                        for match in re.findall(pat, text):
                            objects_found.append({"type": obj_type, "identifier": match, "file": file.name})
                except Exception:
                    continue

        if not objects_found:
            return ToolResult(tool_name=self.name, success=True, output="No explicit game object definitions found.")

        lines = [f"- [{o['type']}] {o['identifier']} in {o['file']}" for o in objects_found]
        return ToolResult(tool_name=self.name, success=True, output="\n".join(lines), data={"objects": objects_found})


# 3. Inspect Components Tool
class InspectComponentsInput(BaseModel):
    file_or_dir: str = Field(default=".", description="File or directory to inspect for components, scripts, or systems")


class InspectComponentsTool(BaseTool):
    name: str = "inspect_components"
    description: str = "Inspect attached components, MonoBehaviour scripts, and game systems."
    args_schema: type[BaseModel] = InspectComponentsInput

    def execute(self, file_or_dir: str = ".") -> ToolResult:
        target = Path(file_or_dir).resolve()
        if not target.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Path not found: {file_or_dir}")

        components: list[dict[str, str]] = []
        files = [target] if target.is_file() else list(target.rglob("*.*"))

        for file in files:
            if any(p.startswith(".") or p in ("node_modules", "dist", "build") for p in file.parts):
                continue
            if file.suffix in (".cs", ".js", ".ts", ".gd"):
                try:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                    # Unity MonoBehaviours
                    for m in re.findall(r"class\s+([A-Za-z0-9_]+)\s*:\s*(?:MonoBehaviour|NetworkBehaviour)", text):
                        components.append({"kind": "Unity Component", "name": m, "file": file.name})
                    # Godot scripts
                    for g in re.findall(r"extends\s+([A-Za-z0-9_]+)", text):
                        if file.suffix == ".gd":
                            components.append({"kind": "Godot Node Script", "name": f"{file.stem} ({g})", "file": file.name})
                    # Custom JS/TS Game Components
                    for c in re.findall(r"class\s+([A-Za-z0-9_]+(?:Component|System|Controller))", text):
                        components.append({"kind": "Component/Controller", "name": c, "file": file.name})
                except Exception:
                    continue

        if not components:
            return ToolResult(tool_name=self.name, success=True, output="No components or controllers detected.")

        lines = [f"- [{c['kind']}] {c['name']} in {c['file']}" for c in components]
        return ToolResult(tool_name=self.name, success=True, output="\n".join(lines), data={"components": components})
