#!/usr/bin/env python
"""
Merge translated chunks into final reading outputs.

Outputs:
- Chinese-only merged markdown
- Bilingual merged markdown

Example:
    python 05_merge.py \
        --manifest work/chunks/generative_ai_labor_demand/manifest.json \
        --translated-dir work/translated/generative_ai_labor_demand \
        --output-zh work/output/generative_ai_labor_demand.zh.md \
        --output-bilingual work/output/generative_ai_labor_demand.bilingual.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


FRONT_MATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Chunk manifest JSON.")
    parser.add_argument("--translated-dir", required=True, type=Path, help="Translated chunk dir.")
    parser.add_argument("--output-zh", required=True, type=Path, help="Merged Chinese markdown.")
    parser.add_argument(
        "--output-bilingual",
        required=True,
        type=Path,
        help="Merged bilingual markdown.",
    )
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="Skip missing translated chunks instead of failing.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1).strip()


def extract_heading(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def load_translation(path: Path) -> str:
    return strip_front_matter(path.read_text(encoding="utf-8"))


def render_heading(level: int, title: str) -> str:
    safe_level = min(max(level, 1), 6)
    return f'{"#" * safe_level} {title}'


def group_chunks_by_heading(chunks: List[Dict]) -> List[List[Dict]]:
    groups: List[List[Dict]] = []
    current_group: List[Dict] = []
    current_key = None

    for item in chunks:
        key = (tuple(item.get("heading_path", [])), item.get("level"))
        if current_group and key != current_key:
            groups.append(current_group)
            current_group = []
        current_group.append(item)
        current_key = key

    if current_group:
        groups.append(current_group)
    return groups


def merge_outputs(manifest: Dict, translated_dir: Path, skip_missing: bool) -> tuple[str, str]:
    zh_parts: List[str] = []
    bilingual_parts: List[str] = []
    chunks = manifest.get("chunks", [])
    mode = manifest.get("mode", "section")

    if mode == "document":
        if not chunks:
            return "", ""
        item = chunks[0]
        source_path = Path(item["source_file"])
        translated_path = translated_dir / source_path.name.replace(".md", ".zh.md")
        if not translated_path.exists():
            if skip_missing:
                return "", ""
            raise FileNotFoundError(f"Missing translated chunk: {translated_path}")
        source_text = source_path.read_text(encoding="utf-8").strip()
        translated_text = load_translation(translated_path)
        bilingual = "\n".join(["## 中文", "", translated_text, "", "## English", "", source_text, ""]).strip()
        return translated_text.strip() + "\n", bilingual + "\n"

    for group in group_chunks_by_heading(chunks):
        first = group[0]
        title = first["title"]
        level = int(first.get("level", 1))
        zh_group_parts: List[str] = [render_heading(level, title), ""]
        en_group_parts: List[str] = [render_heading(level, title), ""]

        for item in group:
            source_path = Path(item["source_file"])
            translated_path = translated_dir / source_path.name.replace(".md", ".zh.md")
            if not translated_path.exists():
                if skip_missing:
                    continue
                raise FileNotFoundError(f"Missing translated chunk: {translated_path}")

            source_text = source_path.read_text(encoding="utf-8").strip()
            translated_text = load_translation(translated_path)
            zh_group_parts.extend([translated_text, ""])
            en_group_parts.extend([source_text, ""])

        zh_parts.append("\n".join(zh_group_parts).strip())
        bilingual_parts.append(
            "\n".join(
                [
                    render_heading(level, title),
                    "",
                    "## 中文",
                    "",
                    "\n\n".join(part for part in zh_group_parts[2:] if part.strip()),
                    "",
                    "## English",
                    "",
                    "\n\n".join(part for part in en_group_parts[2:] if part.strip()),
                ]
            ).strip()
        )

    return "\n\n".join(zh_parts).strip() + "\n", "\n\n".join(bilingual_parts).strip() + "\n"


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    manifest = load_json(args.manifest)
    zh_content, bilingual_content = merge_outputs(
        manifest,
        translated_dir=args.translated_dir,
        skip_missing=args.skip_missing,
    )
    write_output(args.output_zh, zh_content)
    write_output(args.output_bilingual, bilingual_content)
    print(f"Chinese output written to: {args.output_zh}")
    print(f"Bilingual output written to: {args.output_bilingual}")


if __name__ == "__main__":
    main()
