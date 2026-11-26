"""Dynamic loader for global and engine-specific skills (SKILL.md format) and rules."""

from pathlib import Path
from game_agents.core.contracts.project_manifest import EngineType


class SkillsAndRulesLoader:
    """Loads markdown rules and SKILL.md packages for a target game engine."""

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

    def _read_skill_packages(self, directory: Path) -> list[str]:
        """Load SKILL.md from each skill folder; list optional references/ and scripts/ without eagerly reading them."""
        contents: list[str] = []
        if not directory.exists() or not directory.is_dir():
            return contents

        # Support loose .md files if any
        contents.extend(self._read_markdown_dir(directory))

        # Load <skill-name>/SKILL.md directories
        for skill_dir in sorted(d for d in directory.iterdir() if d.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            try:
                text = skill_md.read_text(encoding="utf-8").strip()
                refs = sorted((skill_dir / "references").glob("*.md")) if (skill_dir / "references").is_dir() else []
                scripts = sorted((skill_dir / "scripts").glob("*")) if (skill_dir / "scripts").is_dir() else []

                extras = []
                if refs:
                    extras.append("Optional references (load when needed): " + ", ".join(str(r) for r in refs))
                if scripts:
                    extras.append("Runnable scripts: " + ", ".join(str(s) for s in scripts))

                if extras:
                    text += "\n\n" + "\n".join(extras)
                contents.append(text)
            except Exception:
                continue

        return contents

    def load_reference(self, skill_dir: Path, ref_name: str) -> str | None:
        """Load an optional reference file from <skill_dir>/references/<ref_name> on demand."""
        ref_path = skill_dir / "references" / ref_name
        if ref_path.exists() and ref_path.is_file():
            return ref_path.read_text(encoding="utf-8").strip()
        return None

    def load_for_engine(self, engine: EngineType | str) -> dict[str, list[str]]:
        """Load global rules, engine-specific rules, common skills, and engine skills."""
        engine_name = engine.value if isinstance(engine, EngineType) else str(engine).lower()

        global_rules = self._read_markdown_dir(self.base_dir / "rules" / "global")
        engine_rules = self._read_markdown_dir(self.base_dir / "rules" / engine_name)
        common_skills = self._read_skill_packages(self.base_dir / "skills" / "common")
        engine_skills = self._read_skill_packages(self.base_dir / "skills" / engine_name)

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
