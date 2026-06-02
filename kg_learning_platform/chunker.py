from __future__ import annotations

import re
from typing import List

from .models import Chunk
from .storage import new_id


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
STRUCTURED_BLOCK_RE = re.compile(
    r"<table\b.*?</table>|(?:^\s*\|[^\n]*\|\s*$\n?){2,}|(?<!\\)\$\$.*?(?<!\\)\$\$",
    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


class Chunker:
    def __init__(self, max_chars: int = 900, overlap_chars: int = 120) -> None:
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def split(self, document_id: str, text: str) -> List[Chunk]:
        sections = self._sections(text)
        chunks: List[Chunk] = []
        ordinal = 0
        cursor = 0
        for heading, body in sections:
            for piece, start_offset, end_offset in self._split_body(body):
                ordinal += 1
                chunk = Chunk(
                    id=new_id("chunk"),
                    document_id=document_id,
                    ordinal=ordinal,
                    text=piece,
                    heading=heading,
                    char_start=cursor + start_offset,
                    char_end=cursor + end_offset,
                    chunk_type=self._classify_piece(piece, heading),
                    metadata=self._piece_metadata(piece, heading),
                )
                chunks.append(chunk)
            cursor += len(body)
        return chunks

    def _sections(self, text: str) -> List[tuple[str, str]]:
        sections: List[tuple[str, List[str]]] = [("Document", [])]
        current_heading = "Document"
        for line in text.splitlines():
            match = HEADING_RE.match(line.strip())
            if match:
                current_heading = match.group(2).strip()
                sections.append((current_heading, []))
                continue
            sections[-1][1].append(line)
        return [(heading, "\n".join(lines).strip()) for heading, lines in sections if "\n".join(lines).strip()]

    def _split_body(self, body: str) -> List[tuple[str, int, int]]:
        paragraphs = self._blocks(body)
        pieces: List[tuple[str, int, int]] = []
        current: List[tuple[str, int, int]] = []
        current_start = 0

        for paragraph, start, end in paragraphs:
            projected = len("\n\n".join([block[0] for block in current] + [paragraph]))
            if current and projected > self.max_chars:
                text = "\n\n".join(block[0] for block in current).strip()
                pieces.append((text, current_start, current_start + len(text)))
                if self._is_structured_block(text) or self._is_structured_block(paragraph):
                    current = [(paragraph, start, end)]
                    current_start = start
                else:
                    overlap = text[-self.overlap_chars :] if self.overlap_chars > 0 else ""
                    current = [(overlap, max(0, start - len(overlap)), start), (paragraph, start, end)] if overlap else [(paragraph, start, end)]
                    current_start = current[0][1]
            elif not current:
                current_start = start
                current.append((paragraph, start, end))
            else:
                current.append((paragraph, start, end))

        if current:
            text = "\n\n".join(block[0] for block in current if block[0]).strip()
            pieces.append((text, current_start, current_start + len(text)))

        long_split: List[tuple[str, int, int]] = []
        for text, start, _ in pieces:
            if len(text) <= self.max_chars * 1.5 or self._is_structured_block(text):
                long_split.append((text, start, start + len(text)))
                continue
            step = max(1, self.max_chars - self.overlap_chars)
            for offset in range(0, len(text), step):
                piece = text[offset : offset + self.max_chars].strip()
                if piece:
                    long_split.append((piece, start + offset, start + offset + len(piece)))
        return long_split

    def _blocks(self, body: str) -> List[tuple[str, int, int]]:
        blocks: List[tuple[str, int, int]] = []
        cursor = 0
        for match in STRUCTURED_BLOCK_RE.finditer(body):
            if match.start() > cursor:
                blocks.extend(self._paragraph_blocks(body[cursor : match.start()], offset=cursor))
            block = match.group(0).strip()
            if block:
                leading = len(match.group(0)) - len(match.group(0).lstrip())
                start = match.start() + leading
                blocks.append((block, start, start + len(block)))
            cursor = match.end()
        if cursor < len(body):
            blocks.extend(self._paragraph_blocks(body[cursor:], offset=cursor))
        return blocks

    def _paragraph_blocks(self, text: str, offset: int = 0) -> List[tuple[str, int, int]]:
        blocks: List[tuple[str, int, int]] = []
        for match in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", text):
            paragraph = match.group(0).strip()
            if not paragraph:
                continue
            leading = len(match.group(0)) - len(match.group(0).lstrip())
            start = offset + match.start() + leading
            blocks.append((paragraph, start, start + len(paragraph)))
        return blocks

    def _is_structured_block(self, text: str) -> bool:
        stripped = text.strip()
        return bool(STRUCTURED_BLOCK_RE.fullmatch(stripped))

    def _classify_piece(self, text: str, heading: str = "") -> str:
        lowered = f"{heading}\n{text}".lower()
        if re.search(r"!\[[^\]]*\]\([^)]+\)", text):
            return "image"
        if "<table" in lowered or len(re.findall(r"^\s*\|.+\|\s*$", text, flags=re.MULTILINE)) >= 2:
            return "table"
        if re.search(r"(?<!\\)\$\$|\\begin\{|\\frac|\\sum|\\nabla|\\cdot|\\boldsymbol", text):
            return "formula"
        if any(token in lowered for token in ["例", "example", "习题", "练习", "解：", "算法", "algorithm"]):
            return "example"
        if any(token in lowered for token in ["证明", "proof", "推导", "收敛", "定理"]):
            return "proof"
        return "concept"

    def _piece_metadata(self, text: str, heading: str = "") -> dict:
        return {
            "formula_count": len(re.findall(r"(?<!\\)\$(?!\$).+?(?<!\\)\$", text, flags=re.DOTALL))
            + len(re.findall(r"(?<!\\)\$\$.+?(?<!\\)\$\$", text, flags=re.DOTALL)),
            "image_count": len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text)),
            "table_like": "<table" in text.lower()
            or len(re.findall(r"^\s*\|.+\|\s*$", text, flags=re.MULTILINE)) >= 2,
            "heading": heading,
        }
