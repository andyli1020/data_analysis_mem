from __future__ import annotations

import html
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree

from .config import MinerUConfig
from .mineru import MinerUClient
from .textio import read_text_detected


class DocumentParser:
    """Document parser with lightweight built-in fallbacks.

    V1 prefers local, inspectable parsing. Optional PDF libraries are used when
    installed, while DOCX/PPTX text extraction is handled with standard-library
    zip/XML parsing.
    """

    def __init__(self, mineru_config: MinerUConfig | None = None, mineru_client: MinerUClient | None = None) -> None:
        self.mineru_config = mineru_config or MinerUConfig()
        self.mineru_client = mineru_client

    def parse(
        self,
        path: Path | str,
        backend: str = "basic",
        artifact_dir: Path | str | None = None,
    ) -> Dict[str, object]:
        backend = (backend or "basic").lower()
        if backend in {"basic", "local", "local-v1"}:
            return self._parse_basic(path)
        if backend in {"mineru", "mineru-agent", "mineru-agent-api"}:
            return self._parse_mineru_agent(path)
        if backend in {"mineru-precision", "mineru-precision-api"}:
            return self._parse_mineru_precision(path, artifact_dir=artifact_dir)
        raise ValueError(f"Unsupported parser backend: {backend}")

    def available_backends(self) -> List[Dict[str, object]]:
        return [
            {
                "id": "basic",
                "name": "本地基础解析",
                "available": True,
                "description": "离线可用，适合 Markdown/TXT/普通 PDF/DOCX/PPTX。",
            },
            {
                "id": "mineru",
                "name": "MinerU Agent API",
                "available": self.mineru_config.enabled,
                "description": "适合公式、表格和课件型 PDF；需要外网访问 MinerU Agent API。",
            },
            {
                "id": "mineru-precision",
                "name": "MinerU 精准解析 API",
                "available": self.mineru_config.enabled,
                "requires_token": True,
                "token_configured": bool(os.getenv(self.mineru_config.precision_api_key_env, "").strip()),
                "description": "Token 鉴权，支持 VLM 精准解析和 full.md 结果 zip，适合公式密集 PDF。",
            },
        ]

    def _parse_mineru_agent(self, path: Path | str) -> Dict[str, object]:
        if not self.mineru_config.enabled:
            raise RuntimeError("MinerU parser is disabled in config.")
        client = self.mineru_client or MinerUClient(self.mineru_config)
        parsed = client.parse_file_agent(path)
        return self._mineru_result_to_parsed(path, parsed)

    def _parse_mineru_precision(self, path: Path | str, artifact_dir: Path | str | None = None) -> Dict[str, object]:
        if not self.mineru_config.enabled:
            raise RuntimeError("MinerU parser is disabled in config.")
        client = self.mineru_client or MinerUClient(self.mineru_config)
        parsed = client.parse_file_precision(path, artifact_dir=artifact_dir)
        return self._mineru_result_to_parsed(path, parsed)

    def _mineru_result_to_parsed(self, path: Path | str, parsed: Dict[str, object]) -> Dict[str, object]:
        normalized = self._normalize(str(parsed.get("text") or ""))
        file_path = Path(path)
        metadata = dict(parsed.get("metadata", {}))
        metadata.update(
            {
                "extension": file_path.suffix.lower().lstrip("."),
                "parser": metadata.get("parser", "mineru-agent-api"),
                "char_count": len(normalized),
            }
        )
        return {
            "text": normalized,
            "title": parsed.get("title") or self._infer_title(file_path, normalized),
            "metadata": metadata,
        }

    def _parse_basic(self, path: Path | str) -> Dict[str, object]:
        file_path = Path(path)
        suffix = file_path.suffix.lower()
        encoding = None
        if suffix in {".md", ".txt"}:
            text, encoding = read_text_detected(file_path)
        elif suffix in {".html", ".htm"}:
            text, encoding = self._parse_html(file_path)
        elif suffix == ".ipynb":
            text = self._parse_ipynb(file_path)
        elif suffix == ".docx":
            text = self._parse_docx(file_path)
        elif suffix == ".pptx":
            text = self._parse_pptx(file_path)
        elif suffix == ".pdf":
            text = self._parse_pdf(file_path)
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        normalized = self._normalize(text)
        return {
            "text": normalized,
            "title": self._infer_title(file_path, normalized),
            "metadata": {
                "extension": suffix.lstrip("."),
                "parser": "local-v1",
                "encoding": encoding,
                "char_count": len(normalized),
            },
        }

    def _parse_html(self, path: Path) -> tuple[str, str]:
        text, encoding = read_text_detected(path)
        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return html.unescape(text), encoding

    def _parse_ipynb(self, path: Path) -> str:
        payload = json.loads(path.read_text(encoding="utf-8"))
        parts: List[str] = []
        for cell in payload.get("cells", []):
            source = "".join(cell.get("source", []))
            if not source.strip():
                continue
            prefix = "# Markdown" if cell.get("cell_type") == "markdown" else "# Code"
            parts.append(f"{prefix}\n{source}")
        return "\n\n".join(parts)

    def _parse_docx(self, path: Path) -> str:
        with zipfile.ZipFile(path) as package:
            xml = package.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for para in root.findall(".//w:p", namespace):
            texts = [node.text or "" for node in para.findall(".//w:t", namespace)]
            paragraph = "".join(texts).strip()
            if paragraph:
                paragraphs.append(paragraph)
        return "\n\n".join(paragraphs)

    def _parse_pptx(self, path: Path) -> str:
        slide_texts: List[str] = []
        with zipfile.ZipFile(path) as package:
            slide_names = sorted(name for name in package.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
            for slide_index, name in enumerate(slide_names, start=1):
                root = ElementTree.fromstring(package.read(name))
                texts = [node.text or "" for node in root.iter() if node.tag.endswith("}t")]
                body = "\n".join(text.strip() for text in texts if text and text.strip())
                if body:
                    slide_texts.append(f"# Slide {slide_index}\n{body}")
        return "\n\n".join(slide_texts)

    def _parse_pdf(self, path: Path) -> str:
        try:
            import pdfplumber  # type: ignore

            pages = []
            with pdfplumber.open(path) as pdf:
                for index, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        pages.append(f"[PAGE {index}]\n{text}")
            return "\n\n".join(pages)
        except Exception:
            pass

        try:
            from PyPDF2 import PdfReader  # type: ignore

            reader = PdfReader(str(path))
            pages = []
            for index, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"[PAGE {index}]\n{text}")
            return "\n\n".join(pages)
        except Exception as exc:
            raise RuntimeError(
                f"PDF parsing requires pdfplumber or PyPDF2. Could not parse {path.name}: {exc}"
            ) from exc

    def _normalize(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\ufeff", "").replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _infer_title(self, path: Path, text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if 4 <= len(stripped) <= 120:
                return stripped
        return path.stem
