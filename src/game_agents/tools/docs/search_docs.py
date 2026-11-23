"""Documentation search tool for official game engine docs and APIs."""

import urllib.parse
from pydantic import BaseModel, Field
from game_agents.core.contracts.tool_result import ToolResult
from game_agents.tools.base import BaseTool

OFFICIAL_DOCS_HUBS = {
    "phaser": "https://phaser.io/learn/tutorials",
    "unity": "https://docs.unity3d.com/Manual/index.html",
    "unreal": "https://dev.epicgames.com/documentation/en-us/unreal-engine",
    "godot": "https://docs.godotengine.org/en/stable/",
    "threejs": "https://threejs.org/docs/",
}

ENGINE_QUICK_REFERENCES = {
    "phaser": {
        "physics": "Phaser Arcade Physics: this.physics.add.sprite(x, y, key), setCollideWorldBounds(true), setBounce(0.2).",
        "scene": "Phaser.Scene lifecycle: preload(), create(), update(time, delta).",
        "input": "Input: this.input.keyboard.createCursorKeys(), pointerdown listener: this.input.on('pointerdown', fn).",
        "audio": "Audio: this.sound.add('key'), this.sound.play('key').",
    },
    "godot": {
        "lifecycle": "Node lifecycle: _ready(), _process(delta), _physics_process(delta).",
        "movement": "CharacterBody2D: velocity = dir * speed; move_and_slide().",
    },
    "unity": {
        "lifecycle": "MonoBehaviour: Awake(), Start(), Update(), FixedUpdate().",
        "movement": "Rigidbody: rb.linearVelocity = dir * speed; or rb.AddForce(force, ForceMode.Impulse).",
    },
    "threejs": {
        "setup": "Scene setup: const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(...); const renderer = new THREE.WebGLRenderer();",
        "loop": "Render loop: function animate() { requestAnimationFrame(animate); renderer.render(scene, camera); }",
    },
}


class SearchDocsInput(BaseModel):
    query: str = Field(..., description="Query or API method to search (e.g. 'Arcade Physics collision', 'CharacterController')")
    engine: str = Field(default="phaser", description="Target engine: 'phaser', 'unity', 'unreal', 'godot', 'threejs'")


class SearchDocsTool(BaseTool):
    name: str = "search_docs"
    description: str = "Search official game engine documentation, lifecycle guides, and API references."
    args_schema: type[BaseModel] = SearchDocsInput

    def execute(self, query: str, engine: str = "phaser") -> ToolResult:
        engine_key = engine.lower()
        hub_url = OFFICIAL_DOCS_HUBS.get(engine_key, "https://developer.mozilla.org/en-US/docs/Games")

        # Check offline quick references first
        ref_snippets = []
        if engine_key in ENGINE_QUICK_REFERENCES:
            for topic, text in ENGINE_QUICK_REFERENCES[engine_key].items():
                if any(w in topic.lower() or w in text.lower() for w in query.lower().split()):
                    ref_snippets.append(f"[{topic.upper()}] {text}")

        encoded_q = urllib.parse.quote(f"{engine} {query}")
        search_link = f"https://www.google.com/search?q={encoded_q}"

        lines = [f"Official Docs Hub for {engine.title()}: {hub_url}"]
        if ref_snippets:
            lines.append("Quick Reference Matches:")
            lines.extend(ref_snippets)
        lines.append(f"Direct Search Link: {search_link}")

        return ToolResult(
            tool_name=self.name,
            success=True,
            output="\n".join(lines),
            data={"engine": engine, "hub": hub_url, "matches": ref_snippets},
        )
