"""Phaser-specific agent tools."""

import re
from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class PhaserCreateSceneInput(BaseModel):
    scene_name: str = Field(..., description="PascalCase scene name (e.g. 'PlayScene', 'MainMenuScene')")
    file_path: str = Field(..., description="File path to save the scene (e.g. 'src/scenes/PlayScene.js')")
    include_physics: bool = Field(default=True, description="Whether to include Arcade Physics boilerplate")


class PhaserCreateSceneTool(BaseTool):
    name: str = "phaser_create_scene"
    description: str = "Generate a boilerplate Phaser 3 Scene with preload(), create(), and update() methods."
    args_schema: type[BaseModel] = PhaserCreateSceneInput

    def execute(self, scene_name: str, file_path: str, include_physics: bool = True) -> ToolResult:
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        physics_code = """
        // Arcade Physics setup
        this.physics.world.setBounds(0, 0, 800, 600);
""" if include_physics else ""

        code = f"""class {scene_name} extends Phaser.Scene {{
    constructor() {{
        super({{ key: '{scene_name}' }});
    }}

    preload() {{
        // Load assets here
        // this.load.image('player', 'assets/player.png');
    }}

    create() {{{physics_code}
        // Initialize game objects here
        this.add.text(400, 300, '{scene_name} Active', {{
            fontSize: '32px',
            color: '#ffffff'
        }}).setOrigin(0.5);
    }}

    update(time, delta) {{
        // Game loop updates
    }}
}}

// Export for module or global use
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {scene_name};
}}
"""
        try:
            path.write_text(code, encoding="utf-8")
            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Created Phaser scene '{scene_name}' at {file_path}",
                data={"path": str(path), "scene_name": scene_name},
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to create scene: {str(e)}")


class PhaserInspectConfigInput(BaseModel):
    project_path: str = Field(default=".", description="Path to game project root")


class PhaserInspectConfigTool(BaseTool):
    name: str = "phaser_inspect_config"
    description: str = "Find and parse the Phaser.Game configuration (dimensions, physics, scenes) in the project."
    args_schema: type[BaseModel] = PhaserInspectConfigInput

    def execute(self, project_path: str = ".") -> ToolResult:
        root = Path(project_path).resolve()
        for f in root.rglob("*.js"):
            if any(p.startswith(".") or p == "node_modules" for p in f.parts):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "new Phaser.Game" in content or "Phaser.AUTO" in content:
                    # Extract dimensions
                    w = re.search(r"width:\s*([0-9]+)", content)
                    h = re.search(r"height:\s*([0-9]+)", content)
                    physics = re.search(r"physics:\s*\{[^}]*default:\s*['\"]([^'\"]+)['\"]", content)
                    scenes = re.findall(r"scene:\s*\[([^\]]+)\]", content)

                    summary = [
                        f"Found Phaser Game config in {f.name}:",
                        f"- Resolution: {w.group(1) if w else 'default'} x {h.group(1) if h else 'default'}",
                        f"- Physics engine: {physics.group(1) if physics else 'none'}",
                        f"- Registered scenes: {scenes[0].strip() if scenes else 'single scene/function'}",
                    ]
                    return ToolResult(tool_name=self.name, success=True, output="\n".join(summary))
            except Exception:
                continue

        return ToolResult(tool_name=self.name, success=True, output="No explicit Phaser.Game config found.")
