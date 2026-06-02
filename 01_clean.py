#!/usr/bin/env python
"""
Clean noisy markdown text extracted from academic PDFs.

The script targets OCR / PDF-extraction artifacts commonly found in papers:
- page separators and isolated page numbers
- bold-wrapped section headings
- footnote text glued to the first token
- hard line wraps inside paragraphs
- obvious spacing issues around punctuation

Example:
    python 01_clean.py \
        --input papers/Generative_AI_and_the_Reorganization_of_Labor_Demand_ref.md \
        --output work/clean/generative_ai_labor_demand.clean.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List


TITLE_HINTS = {
    "abstract",
    "keywords",
}

SECTION_RE = re.compile(
    r"^\*\*(?P<label>(?:\d+(?:\.\d+)*)|Appendix(?:\s+[A-Z])?)\s+(?P<title>.+?)\*\*$"
)
APPENDIX_RE = re.compile(r"^\*\*Appendix(?:\s+[A-Z])?\s+.+?\*\*$")
EMPHASIZED_RE = re.compile(r"^\*\*(.+?)\*\*$")
PLAIN_SECTION_RE = re.compile(r"^(?P<label>\d+(?:\.\d+)*)\s+(?P<title>.+)$")
PLAIN_APPENDIX_RE = re.compile(r"^Appendix(?:\s+[A-Z])?(?:\s+.+)?$", re.IGNORECASE)
PAGE_MARKER_RE = re.compile(r"^\[PAGE\s+\d+\]$", re.IGNORECASE)
PAGE_NUM_RE = re.compile(r"^\*?\*?\d+\*?\*?$")
CAPTION_RE = re.compile(r"^(Figure|Table)\s+[A-Za-z0-9.-]+\s*:", re.IGNORECASE)
NOISE_TOKEN_RE = re.compile(r"^[\[\]\(\)\.\-_/A-Za-z0-9]{1,24}$")
LINE_NUMBER_PREFIX_RE = re.compile(r"^\s*\d+\u2192")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Raw extracted markdown file.")
    parser.add_argument("--output", required=True, type=Path, help="Cleaned markdown output path.")
    parser.add_argument(
        "--drop-appendices",
        action="store_true",
        help="Stop at the first appendix heading and keep only the main paper.",
    )
    return parser.parse_args()


def strip_line_number_prefix(text: str) -> str:
    return "\n".join(LINE_NUMBER_PREFIX_RE.sub("", line) for line in text.splitlines())


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_line_number_prefix(text)
    text = text.replace("\u00a0", " ")
    text = text.replace("\ufeff", "")
    return text


def is_separator(line: str) -> bool:
    return line.strip() == "---"


def is_page_marker(line: str) -> bool:
    return bool(PAGE_MARKER_RE.fullmatch(line.strip()))


def is_page_number(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return bool(PAGE_NUM_RE.fullmatch(stripped))


def is_caption_line(line: str) -> bool:
    return bool(CAPTION_RE.match(line.strip()))


def is_plain_appendix_heading(line: str) -> bool:
    stripped = line.strip()
    if not PLAIN_APPENDIX_RE.match(stripped):
        return False
    if len(stripped.split()) > 8:
        return False
    return True


def is_short_noise_fragment(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    parts = stripped.split()
    if len(parts) <= 3 and any(ch in stripped for ch in "[]") and len(stripped) <= 24:
        return True
    if len(parts) == 1 and stripped.isalpha() and len(stripped) <= 8:
        if not (stripped.islower() or stripped.isupper() or stripped.istitle()):
            return True
    return False


def is_obvious_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if (
        APPENDIX_RE.match(stripped)
        or SECTION_RE.match(stripped)
        or is_plain_appendix_heading(stripped)
        or stripped.lower() == "abstract"
        or stripped.lower().startswith("keywords:")
    ):
        return False
    if is_caption_line(stripped):
        return False
    if is_short_noise_fragment(stripped):
        return True
    if stripped.startswith("**") and stripped.endswith("**"):
        inner = stripped[2:-2].strip()
        if inner.lower() in TITLE_HINTS:
            return False
        if 1 <= len(inner) <= 24 and NOISE_TOKEN_RE.fullmatch(inner):
            has_vowel = bool(re.search(r"[aeiouAEIOU]", inner))
            has_digit = any(ch.isdigit() for ch in inner)
            if has_digit or not has_vowel:
                return True
    return False


def classify_heading(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None

    lowered = stripped.lower()
    if lowered == "**abstract**":
        return "# Abstract"
    if lowered == "abstract":
        return "# Abstract"
    if lowered.startswith("**keywords:") and stripped.endswith("**"):
        return "## " + stripped[2:-2].strip()
    if lowered.startswith("keywords:"):
        return "## " + stripped

    section_match = SECTION_RE.match(stripped)
    if section_match:
        label = section_match.group("label")
        title = section_match.group("title").strip()
        level = 1 if "." not in label and not label.lower().startswith("appendix") else 2
        return f'{"#" * level} {label} {title}'

    if APPENDIX_RE.match(stripped):
        return "## " + stripped[2:-2].strip()
    if is_plain_appendix_heading(stripped):
        return "## " + stripped

    plain_section_match = PLAIN_SECTION_RE.match(stripped)
    if plain_section_match and len(stripped.split()) <= 12:
        label = plain_section_match.group("label")
        title = plain_section_match.group("title").strip()
        if not title or not title[0].isupper():
            return None
        level = 1 if "." not in label else 2
        return f'{"#" * level} {label} {title}'

    emphasized = EMPHASIZED_RE.match(stripped)
    if emphasized:
        inner = emphasized.group(1).strip()
        if inner.lower() in TITLE_HINTS:
            return "# " + inner.title()
    return None


def fix_inline_spacing(text: str) -> str:
    # Repair punctuation spacing introduced by extraction.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([A-Za-z0-9(])", r"\1 \2", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def repair_footnote_prefix(line: str) -> str:
    match = re.match(r"^(\d{1,2})([A-Za-z])", line)
    if not match:
        return line
    number = match.group(1)
    body = line[len(number) :]
    return f"[Footnote {number}] {body}"


def trim_front_matter_acknowledgement(line: str) -> str:
    if ("∗" in line or "*" in line) and "gratefully acknowledges" in line.lower():
        marker_positions = [pos for pos in (line.find("∗"), line.find("*")) if pos != -1]
        if marker_positions:
            line = line[: min(marker_positions)].rstrip()
    return line


def is_front_matter_note_line(line: str) -> bool:
    lowered = re.sub(r"\s+", "", line.lower())
    markers = [
        "gratefullyacknowledges",
        "wethank",
        "wearealsograteful",
        "seminarparticipants",
        "anyerrorsareourown",
    ]
    return any(marker in lowered for marker in markers)


def is_noise_footnote_line(line: str) -> bool:
    if not line.startswith("[Footnote "):
        return False
    _, _, body = line.partition("]")
    body = body.strip()
    if not body:
        return True
    tokens = body.split()
    if len(tokens) <= 4:
        odd_token_count = sum(
            1
            for token in tokens
            if any(ch.isalpha() for ch in token)
            and not (token.islower() or token.isupper() or token.istitle())
        )
        if odd_token_count >= 1 and any(ch.isdigit() for ch in body):
            return True
    return False


def should_force_break(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if is_caption_line(stripped):
        return True
    if stripped.startswith("[Footnote "):
        return True
    return False


def flush_paragraph(buffer: List[str], output: List[str]) -> None:
    if not buffer:
        return
    merged: List[str] = []
    for part in buffer:
        part = part.strip()
        if not part:
            continue
        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + part
        else:
            merged.append(part)
    if not merged:
        buffer.clear()
        return
    paragraph = " ".join(merged)
    paragraph = fix_inline_spacing(paragraph)
    if paragraph:
        output.append(paragraph)
    buffer.clear()


def clean_lines(lines: Iterable[str], drop_appendices: bool) -> List[str]:
    output: List[str] = []
    paragraph_buffer: List[str] = []
    seen_appendix = False
    in_front_matter = True

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_paragraph(paragraph_buffer, output)
            if output and output[-1] != "":
                output.append("")
            continue

        if is_separator(line) or is_page_marker(line) or is_page_number(line) or is_obvious_noise(line):
            flush_paragraph(paragraph_buffer, output)
            continue

        heading = classify_heading(line)
        if heading:
            if "Appendix" in heading:
                seen_appendix = True
            if re.match(r"^#\s+\d+", heading):
                in_front_matter = False
            if drop_appendices and seen_appendix:
                break
            flush_paragraph(paragraph_buffer, output)
            if output and output[-1] != "":
                output.append("")
            output.append(heading)
            output.append("")
            continue

        if is_caption_line(line):
            flush_paragraph(paragraph_buffer, output)
            output.append(f"### {fix_inline_spacing(line)}")
            output.append("")
            continue

        line = trim_front_matter_acknowledgement(line)
        line = repair_footnote_prefix(line)

        if in_front_matter and is_front_matter_note_line(line):
            flush_paragraph(paragraph_buffer, output)
            continue

        if is_noise_footnote_line(line):
            flush_paragraph(paragraph_buffer, output)
            continue

        if should_force_break(line):
            flush_paragraph(paragraph_buffer, output)
            output.append(fix_inline_spacing(line))
            output.append("")
            continue

        paragraph_buffer.append(line)

    flush_paragraph(paragraph_buffer, output)

    # Collapse repeated empty lines.
    normalized_output: List[str] = []
    empty_run = 0
    for line in output:
        if line == "":
            empty_run += 1
            if empty_run <= 1:
                normalized_output.append(line)
        else:
            empty_run = 0
            normalized_output.append(line.rstrip())
    while normalized_output and normalized_output[-1] == "":
        normalized_output.pop()
    return normalized_output


def main() -> None:
    args = parse_args()
    raw_text = args.input.read_text(encoding="utf-8")
    normalized = normalize_text(raw_text)
    cleaned_lines = clean_lines(normalized.splitlines(), drop_appendices=args.drop_appendices)
    output_text = "\n".join(cleaned_lines) + "\n"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text, encoding="utf-8")

    print(f"Cleaned markdown written to: {args.output}")
    print(f"Input lines: {len(normalized.splitlines())}")
    print(f"Output lines: {len(cleaned_lines)}")


if __name__ == "__main__":
    main()
