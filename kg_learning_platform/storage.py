from __future__ import annotations

import json
import shutil
import hashlib
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Type, TypeVar
from uuid import uuid4

from .models import Chunk, Document, GraphEdge, GraphNode, LearningArtifact

T = TypeVar("T")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dataclass_from_dict(cls: Type[T], payload: Dict[str, Any]) -> T:
    names = {field.name for field in fields(cls)}
    return cls(**{key: value for key, value in payload.items() if key in names})


class JsonStorage:
    """Small local storage layer for the V1 modular monolith.

    It intentionally uses transparent JSON files so early iterations are easy
    to inspect and migrate to PostgreSQL/Neo4j/Qdrant later.
    """

    def __init__(self, root: Path | str = "kg_store") -> None:
        self.root = Path(root)
        self.documents_dir = self.root / "documents"
        self.chunks_dir = self.root / "chunks"
        self.index_dir = self.root / "index"
        self.graph_dir = self.root / "graph"
        self.artifacts_dir = self.root / "artifacts"
        self.parsed_dir = self.root / "parsed"
        self.meta_dir = self.root / "metadata"
        for directory in [
            self.documents_dir,
            self.chunks_dir,
            self.index_dir,
            self.graph_dir,
            self.artifacts_dir,
            self.parsed_dir,
            self.meta_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def documents_json(self) -> Path:
        return self.meta_dir / "documents.json"

    @property
    def chunks_json(self) -> Path:
        return self.chunks_dir / "chunks.json"

    @property
    def graph_json(self) -> Path:
        return self.graph_dir / "graph.json"

    @property
    def index_json(self) -> Path:
        return self.index_dir / "index.json"

    @property
    def artifacts_json(self) -> Path:
        return self.meta_dir / "learning_artifacts.json"

    @property
    def parse_history_json(self) -> Path:
        return self.meta_dir / "parse_history.json"

    def save_uploaded_file(self, source_path: Path | str, filename: str | None = None) -> Document:
        source = Path(source_path)
        document_id = new_id("doc")
        safe_name = filename or source.name
        target = self.documents_dir / f"{document_id}_{safe_name}"
        shutil.copyfile(source, target)
        document = Document(
            id=document_id,
            filename=safe_name,
            stored_path=str(target),
            content_type=source.suffix.lower().lstrip(".") or "binary",
            created_at=utc_now(),
            metadata={"file_sha256": self.file_sha256(target)},
        )
        documents = self.list_documents()
        documents.append(document)
        self.save_documents(documents)
        return document

    def save_upload_bytes(self, data: bytes, filename: str, content_type: str = "") -> Document:
        document_id = new_id("doc")
        safe_name = Path(filename).name
        target = self.documents_dir / f"{document_id}_{safe_name}"
        target.write_bytes(data)
        document = Document(
            id=document_id,
            filename=safe_name,
            stored_path=str(target),
            content_type=content_type or Path(filename).suffix.lower().lstrip(".") or "binary",
            created_at=utc_now(),
            metadata={"file_sha256": self.file_sha256(target)},
        )
        documents = self.list_documents()
        documents.append(document)
        self.save_documents(documents)
        return document

    def list_documents(self) -> List[Document]:
        return [
            dataclass_from_dict(Document, item)
            for item in read_json(self.documents_json, [])
        ]

    def save_documents(self, documents: Iterable[Document]) -> None:
        write_json(self.documents_json, [document.to_dict() for document in documents])

    def get_document(self, document_id: str) -> Document:
        for document in self.list_documents():
            if document.id == document_id:
                return document
        raise KeyError(f"Document not found: {document_id}")

    def update_document(self, document: Document) -> None:
        documents = self.list_documents()
        updated = False
        for index, existing in enumerate(documents):
            if existing.id == document.id:
                documents[index] = document
                updated = True
                break
        if not updated:
            documents.append(document)
        self.save_documents(documents)

    def delete_document(self, document_id: str) -> None:
        document_path = None
        try:
            document_path = Path(self.get_document(document_id).stored_path)
        except KeyError:
            document_path = None
        documents = [document for document in self.list_documents() if document.id != document_id]
        self.save_documents(documents)
        chunks = [chunk for chunk in self.list_chunks() if chunk.document_id != document_id]
        self.save_chunks(chunks)
        if document_path and document_path.exists() and document_path.is_file():
            document_path.unlink()
        parsed_path = self.document_parsed_dir(document_id)
        if parsed_path.exists():
            shutil.rmtree(parsed_path)

    def document_parsed_dir(self, document_id: str, parser_backend: str | None = None) -> Path:
        base = self.parsed_dir / document_id
        return base / parser_backend if parser_backend else base

    def file_sha256(self, path: Path | str) -> str:
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def list_chunks(self) -> List[Chunk]:
        return [dataclass_from_dict(Chunk, item) for item in read_json(self.chunks_json, [])]

    def save_chunks(self, chunks: Iterable[Chunk]) -> None:
        write_json(self.chunks_json, [chunk.to_dict() for chunk in chunks])

    def replace_document_chunks(self, document_id: str, chunks: Iterable[Chunk]) -> None:
        current = [chunk for chunk in self.list_chunks() if chunk.document_id != document_id]
        current.extend(chunks)
        self.save_chunks(current)

    def list_document_chunks(self, document_id: str) -> List[Chunk]:
        return sorted(
            [chunk for chunk in self.list_chunks() if chunk.document_id == document_id],
            key=lambda chunk: chunk.ordinal,
        )

    def save_graph(self, nodes: Iterable[GraphNode], edges: Iterable[GraphEdge]) -> None:
        write_json(
            self.graph_json,
            {
                "nodes": [node.to_dict() for node in nodes],
                "edges": [edge.to_dict() for edge in edges],
            },
        )

    def load_graph(self) -> tuple[List[GraphNode], List[GraphEdge]]:
        payload = read_json(self.graph_json, {"nodes": [], "edges": []})
        return (
            [dataclass_from_dict(GraphNode, item) for item in payload.get("nodes", [])],
            [dataclass_from_dict(GraphEdge, item) for item in payload.get("edges", [])],
        )

    def save_index(self, payload: Dict[str, Any]) -> None:
        write_json(self.index_json, payload)

    def load_index(self) -> Dict[str, Any]:
        return read_json(self.index_json, {})

    def list_artifacts(self) -> List[LearningArtifact]:
        return [
            dataclass_from_dict(LearningArtifact, item)
            for item in read_json(self.artifacts_json, [])
        ]

    def save_artifacts(self, artifacts: Iterable[LearningArtifact]) -> None:
        write_json(self.artifacts_json, [artifact.to_dict() for artifact in artifacts])

    def add_artifact(self, artifact: LearningArtifact) -> None:
        artifacts = self.list_artifacts()
        artifacts.append(artifact)
        self.save_artifacts(artifacts)

    def get_artifact(self, artifact_id: str) -> LearningArtifact:
        for artifact in self.list_artifacts():
            if artifact.id == artifact_id:
                return artifact
        raise KeyError(f"Learning artifact not found: {artifact_id}")

    def delete_artifact(self, artifact_id: str) -> None:
        artifacts = []
        for artifact in self.list_artifacts():
            if artifact.id == artifact_id:
                path = Path(artifact.path)
                if path.exists() and path.is_file():
                    path.unlink()
                continue
            artifacts.append(artifact)
        self.save_artifacts(artifacts)

    def clear_artifacts(self) -> int:
        artifacts = self.list_artifacts()
        for artifact in artifacts:
            path = Path(artifact.path)
            if path.exists() and path.is_file():
                path.unlink()
        self.save_artifacts([])
        return len(artifacts)

    def add_parse_history(self, entry: Dict[str, Any]) -> None:
        history = self.list_parse_history()
        history.append(entry)
        write_json(self.parse_history_json, history)

    def list_parse_history(self, document_id: str | None = None) -> List[Dict[str, Any]]:
        history = read_json(self.parse_history_json, [])
        if document_id is None:
            return history
        return [entry for entry in history if entry.get("document_id") == document_id]

    def list_parsed_assets(self, document_id: str) -> List[Dict[str, Any]]:
        root = self.document_parsed_dir(document_id)
        if not root.exists():
            return []
        assets = []
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(root).as_posix()
            assets.append(
                {
                    "path": str(path),
                    "relative_path": relative,
                    "size": path.stat().st_size,
                    "extension": path.suffix.lower().lstrip("."),
                    "kind": self._asset_kind(path),
                }
            )
        return assets

    def resolve_parsed_asset(self, document_id: str, relative_path: str) -> Path:
        parts = [
            part
            for part in str(relative_path).replace("\\", "/").split("/")
            if part and part != "."
        ]
        if not parts or any(part == ".." for part in parts):
            raise ValueError("Invalid parsed asset path.")
        root = self.document_parsed_dir(document_id).resolve()
        target = (root / Path(*parts)).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError("Parsed asset path escapes document directory.") from exc
        if not target.is_file():
            raise FileNotFoundError(f"Parsed asset not found: {relative_path}")
        return target

    def _asset_kind(self, path: Path) -> str:
        extension = path.suffix.lower().lstrip(".")
        if extension in {"png", "jpg", "jpeg", "gif", "webp", "bmp"}:
            return "image"
        if extension in {"md", "markdown"}:
            return "markdown"
        if extension in {"json", "jsonl"}:
            return "json"
        if extension == "pdf":
            return "pdf"
        if extension == "zip":
            return "archive"
        return "file"
