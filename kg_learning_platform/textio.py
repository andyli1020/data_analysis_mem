from __future__ import annotations

from pathlib import Path
from typing import Iterable


COMMON_ENCODINGS = ("utf-8", "utf-8-sig", "gb18030", "gbk", "big5", "cp1252", "latin-1")


def decode_bytes(data: bytes, encodings: Iterable[str] = COMMON_ENCODINGS) -> tuple[str, str]:
    best_text = ""
    best_encoding = "utf-8"
    best_score = -1
    for encoding in encodings:
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        score = _text_score(text)
        if score > best_score:
            best_text = text
            best_encoding = encoding
            best_score = score
    if best_text:
        return best_text, best_encoding
    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def read_text_detected(path: Path | str) -> tuple[str, str]:
    return decode_bytes(Path(path).read_bytes())


def _text_score(text: str) -> int:
    replacement_penalty = text.count("\ufffd") * 20
    cjk_bonus = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    ascii_bonus = sum(1 for char in text if char.isascii() and (char.isalnum() or char.isspace()))
    control_penalty = sum(1 for char in text if ord(char) < 32 and char not in "\n\r\t") * 10
    mojibake_penalty = text.count("�") * 20 + text.count("锟") * 12 + text.count("Ã") * 6
    return cjk_bonus * 3 + ascii_bonus - replacement_penalty - control_penalty - mojibake_penalty
