"""Dynamic loader for global and engine-specific skills and rules."""

from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType


class SkillsAndRulesLoader:
    """Loads markdown skills and rules for a target game engine."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent

    def _read_markdown_dir(self, directory: Path) -> list[str]:
        contents: list[str] = []
        if not directory.exists() or not directory.is_dir():
            return contents
        for md_file in sorted(directory.glob("*.md")):
            try:
                text = md_file.read_text(encoding="utf-8").strip()
                if text:
                    contents.append(text)
            except Exception:
                continue
        return contents

    def load_for_engine(self, engine: EngineType | str) -> dict[str, list[str]]:
        """Load global rules, engine-specific rules, common skills, and engine skills."""
        engine_name = engine.value if isinstance(engine, EngineType) else str(engine).lower()

        global_rules = self._read_markdown_dir(self.base_dir / "rules" / "global")
        engine_rules = self._read_markdown_dir(self.base_dir / "rules" / engine_name)
        common_skills = self._read_markdown_dir(self.base_dir / "skills" / "common")
        engine_skills = self._read_markdown_dir(self.base_dir / "skills" / engine_name)

        return {
            "global_rules": global_rules,
            "engine_rules": engine_rules,
            "common_skills": common_skills,
            "engine_skills": engine_skills,
        }

    def format_context(self, engine: EngineType | str) -> str:
        """Format loaded skills and rules into a single prompt-ready context block."""
        loaded = self.load_for_engine(engine)
        sections: list[str] = []
        for label, items in [
            ("Global Rules", loaded["global_rules"]),
            (f"{str(engine).upper()} Rules", loaded["engine_rules"]),
            ("Common Skills", loaded["common_skills"]),
            (f"{str(engine).upper()} Skills", loaded["engine_skills"]),
        ]:
            if items:
                sections.append(f"## {label}\n" + "\n\n".join(items))
        return "\n\n".join(sections) if sections else "No specialized rules or skills loaded."
