"""Three.js-specific agent tools."""

from pathlib import Path
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool


class ThreejsInspectCanvasInput(BaseModel):
    project_path: str = Field(default=".", description="Path to game project root")


class ThreejsInspectCanvasTool(BaseTool):
    name: str = "threejs_inspect_canvas"
    description: str = "Inspect WebGL canvas configuration, lighting, and camera setup in Three.js code."
    args_schema: type[BaseModel] = ThreejsInspectCanvasInput

    def execute(self, project_path: str = ".") -> ToolResult:
        root = Path(project_path).resolve()
        findings = []

        for f in root.rglob("*.js"):
            if any(p.startswith(".") or p == "node_modules" for p in f.parts):
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
                if "THREE.WebGLRenderer" in text:
                    findings.append(f"WebGLRenderer initialized in {f.name}")
                if "PerspectiveCamera" in text:
                    findings.append(f"PerspectiveCamera found in {f.name}")
                if "AmbientLight" in text or "DirectionalLight" in text:
                    findings.append(f"Lighting configured in {f.name}")
                if "GLTFLoader" in text:
                    findings.append(f"GLTF 3D model loader configured in {f.name}")
            except Exception:
                continue

        if not findings:
            return ToolResult(tool_name=self.name, success=True, output="No Three.js canvas setup detected.")

        return ToolResult(tool_name=self.name, success=True, output="\n".join(f"- {item}" for item in findings))


class ThreejsValidateShadersInput(BaseModel):
    shader_path: str = Field(..., description="Path to GLSL vertex (.vert) or fragment (.frag) shader")


class ThreejsValidateShadersTool(BaseTool):
    name: str = "threejs_validate_shaders"
    description: str = "Validate GLSL vertex and fragment shader syntax."
    args_schema: type[BaseModel] = ThreejsValidateShadersInput

    def execute(self, shader_path: str) -> ToolResult:
        p = Path(shader_path).resolve()
        if not p.exists():
            return ToolResult(tool_name=self.name, success=False, error=f"Shader not found: {shader_path}")

        try:
            content = p.read_text(encoding="utf-8")
            if "void main()" not in content:
                return ToolResult(tool_name=self.name, success=False, error="Shader missing 'void main()' entry function.")

            return ToolResult(
                tool_name=self.name,
                success=True,
                output=f"Shader '{p.name}' basic syntax check passed ({len(content.splitlines())} lines).",
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=f"Failed to validate shader: {str(e)}")
