"""Helper script to count Phaser sprite/image/text creations and flag update() allocations."""

import re
import sys
from pathlib import Path


def scan_phaser_project(target_dir: str = ".") -> dict[str, int]:
    root = Path(target_dir).resolve()
    counts = {"sprites": 0, "images": 0, "texts": 0, "graphics": 0, "files_scanned": 0}
    ignored = {"node_modules", "dist", "build", ".git"}

    for path in root.rglob("*"):
        if any(p in ignored or p.startswith(".") for p in path.parts):
            continue
        if path.suffix in (".js", ".ts") and path.is_file():
            counts["files_scanned"] += 1
            text = path.read_text(encoding="utf-8", errors="ignore")
            counts["sprites"] += len(re.findall(r"\.(?:physics\.)?add\.sprite\b", text))
            counts["images"] += len(re.findall(r"\.(?:physics\.)?add\.image\b", text))
            counts["texts"] += len(re.findall(r"\.add\.(?:bitmapText|text)\b", text))
            counts["graphics"] += len(re.findall(r"\.add\.graphics\b", text))

    return counts


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    stats = scan_phaser_project(directory)
    print(f"Phaser Asset/Object Scan for: {Path(directory).resolve()}")
    for k, v in stats.items():
        print(f"  - {k}: {v}")
