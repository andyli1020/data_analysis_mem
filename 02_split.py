#!/usr/bin/env python
"""
Split cleaned markdown into reusable translation chunks.

The splitter preserves heading hierarchy, writes one markdown file per chunk,
and emits a machine-readable manifest for downstream glossary, translation,
and merge steps.

Example:
    python 02_split.py \
        --input work/clean/generative_ai_labor_demand.clean.md \
        --output-dir work/chunks/generative_ai_labor_demand \
        --max-chars 3600
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class Block:
    heading_path: List[str]
    level: int
    title: str
    paragraphs: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Clean markdown input file.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Chunk output directory.")
    parser.add_argument(
        "--mode",
        choices=["section", "chunked", "document"],
        default="section",
        help="How to split the file: section=one chunk per heading block, chunked=split long blocks, document=single chunk for whole file.",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=3600,
        help="Approximate maximum characters per chunk.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=1200,
        help="Minimum characters before forcing a new chunk when possible.",
    )
    parser.add_argument(
        "--include-appendices",
        action="store_true",
        help="Keep appendix sections. Default behavior skips them.",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "section"


def read_blocks(text: str, include_appendices: bool) -> List[Block]:
    lines = text.splitlines()
    blocks: List[Block] = []
    heading_stack: List[str] = []
    current_title = "Front Matter"
    current_level = 1
    current_paragraphs: List[str] = []

    def flush_current() -> None:
        nonlocal current_paragraphs, current_title, current_level
        if not current_paragraphs:
            return
        blocks.append(
            Block(
                heading_path=heading_stack.copy() or [current_title],
                level=current_level,
                title=current_title,
                paragraphs=current_paragraphs.copy(),
            )
        )
        current_paragraphs = []

    for line in lines:
        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            heading_text = heading_match.group(2).strip()
            if heading_text.lower().startswith("appendix") and not include_appendices:
                flush_current()
                break

            flush_current()
            level = len(heading_match.group(1))
            while len(heading_stack) >= level:
                heading_stack.pop()
            heading_stack.append(heading_text)
            current_title = heading_text
            current_level = level
            continue

        if line.strip():
            current_paragraphs.append(line.rstrip())
        elif current_paragraphs and current_paragraphs[-1] != "":
            current_paragraphs.append("")

    flush_current()
    return [block for block in blocks if any(p.strip() for p in block.paragraphs)]


def chunk_block(block: Block, max_chars: int, min_chars: int) -> List[str]:
    chunks: List[str] = []
    current_parts: List[str] = []
    current_len = 0

    paragraphs = [p for p in "\n".join(block.paragraphs).split("\n\n") if p.strip()]

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        para_len = len(paragraph)
        projected = current_len + para_len + (2 if current_parts else 0)

        if current_parts and projected > max_chars and current_len >= min_chars:
            chunks.append("\n\n".join(current_parts))
            current_parts = [paragraph]
            current_len = para_len
            continue

        if para_len > max_chars and not current_parts:
            sentence_parts = split_large_paragraph(paragraph, max_chars)
            for piece in sentence_parts[:-1]:
                chunks.append(piece)
            tail = sentence_parts[-1]
            current_parts = [tail]
            current_len = len(tail)
            continue

        current_parts.append(paragraph)
        current_len = projected

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def split_large_paragraph(paragraph: str, max_chars: int) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    pieces: List[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        projected = len(current) + len(sentence) + (1 if current else 0)
        if current and projected > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces or [paragraph]


def build_document_chunk(text: str) -> Block:
    paragraphs = [line.rstrip() for line in text.splitlines()]
    return Block(
        heading_path=["Document"],
        level=1,
        title="Document",
        paragraphs=paragraphs,
    )


def write_chunks(
    blocks: List[Block],
    output_dir: Path,
    max_chars: int,
    min_chars: int,
    mode: str,
    original_text: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries = []
    chunk_index = 1

    if mode == "document":
        blocks_to_write = [build_document_chunk(original_text)]
    else:
        blocks_to_write = blocks

    for block in blocks_to_write:
        if mode == "chunked":
            chunk_texts = chunk_block(block, max_chars=max_chars, min_chars=min_chars)
        else:
            chunk_texts = ["\n\n".join(p for p in block.paragraphs if p is not None).strip()]

        for part_index, chunk_body in enumerate(chunk_texts, start=1):
            chunk_id = f"chunk_{chunk_index:03d}"
            title_slug = slugify(block.title)[:48]
            filename = f"{chunk_id}_{title_slug}_p{part_index}.md"
            chunk_path = output_dir / filename
            heading_path = " > ".join(block.heading_path)
            chunk_content = chunk_body.strip() + "\n"
            chunk_path.write_text(chunk_content, encoding="utf-8")

            manifest_entries.append(
                {
                    "chunk_id": chunk_id,
                    "title": block.title,
                    "heading_path": block.heading_path,
                    "heading_path_text": heading_path,
                    "level": block.level,
                    "source_file": str(chunk_path),
                    "char_count": len(chunk_body),
                    "part_index": part_index,
                    "body_includes_heading": mode == "document",
                }
            )
            chunk_index += 1

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "mode": mode,
                "chunk_count": len(manifest_entries),
                "max_chars": max_chars,
                "min_chars": min_chars,
                "chunks": manifest_entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


def main() -> None:
    args = parse_args()
    text = args.input.read_text(encoding="utf-8")
    blocks = read_blocks(text, include_appendices=args.include_appendices)
    manifest_path = write_chunks(
        blocks,
        output_dir=args.output_dir,
        max_chars=args.max_chars,
        min_chars=args.min_chars,
        mode=args.mode,
        original_text=text,
    )
    print(f"Chunk manifest written to: {manifest_path}")
    print(f"Blocks parsed: {len(blocks)}")


if __name__ == "__main__":
    main()
