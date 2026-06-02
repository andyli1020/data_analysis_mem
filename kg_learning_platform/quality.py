from __future__ import annotations

import re
from typing import Any, Dict


def build_parse_quality_report(text: str, chunk_count: int = 0) -> Dict[str, Any]:
    replacement_count = text.count("\ufffd")
    mojibake_count = text.count("锟")
    suspicious_question_count = len(re.findall(r"(?<![A-Za-z0-9])\?{2,}(?![A-Za-z0-9])", text))
    formula_inline_count = len(re.findall(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$", text, flags=re.DOTALL))
    formula_block_count = len(re.findall(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", text, flags=re.DOTALL))
    markdown_image_count = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
    html_table_count = len(re.findall(r"<table\b", text, flags=re.IGNORECASE))
    markdown_table_count = len(re.findall(r"^\s*\|.+\|\s*$", text, flags=re.MULTILINE))
    heading_count = len(re.findall(r"^\s{0,3}#{1,6}\s+", text, flags=re.MULTILINE))
    page_marker_count = len(re.findall(r"\[PAGE\s+\d+\]|^#\s*Slide\s+\d+", text, flags=re.IGNORECASE | re.MULTILINE))
    non_whitespace_count = len(re.sub(r"\s+", "", text))
    suspicious_total = replacement_count + mojibake_count + suspicious_question_count
    suspicious_ratio = suspicious_total / max(non_whitespace_count, 1)
    score = 100
    score -= min(35, suspicious_total * 3)
    if non_whitespace_count < 200:
        score -= 20
    if formula_inline_count + formula_block_count == 0 and any(token in text for token in ("公式", "损失函数", "梯度")):
        score -= 8
    if markdown_image_count == 0 and "images/" in text:
        score -= 5
    score = max(0, min(100, score))
    return {
        "char_count": len(text),
        "non_whitespace_count": non_whitespace_count,
        "chunk_count": chunk_count,
        "heading_count": heading_count,
        "page_marker_count": page_marker_count,
        "formula_inline_count": formula_inline_count,
        "formula_block_count": formula_block_count,
        "formula_count": formula_inline_count + formula_block_count,
        "markdown_image_count": markdown_image_count,
        "markdown_table_line_count": markdown_table_count,
        "html_table_count": html_table_count,
        "table_count": html_table_count + (1 if markdown_table_count >= 2 else 0),
        "replacement_char_count": replacement_count,
        "mojibake_marker_count": mojibake_count,
        "suspicious_question_count": suspicious_question_count,
        "suspicious_ratio": round(suspicious_ratio, 6),
        "quality_score": score,
    }
