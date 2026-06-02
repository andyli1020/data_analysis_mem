from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    id: str
    filename: str
    stored_path: str
    content_type: str
    status: str = "uploaded"
    created_at: str = ""
    parsed_at: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Chunk:
    id: str
    document_id: str
    ordinal: int
    text: str
    heading: str = ""
    char_start: int = 0
    char_end: int = 0
    chunk_type: str = "concept"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphNode:
    id: str
    label: str
    type: str
    mentions: int = 0
    source_chunk_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    source: str
    target: str
    type: str
    evidence_chunk_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SearchResult:
    chunk: Chunk
    score: float
    document: Optional[Document] = None
    graph_nodes: List[GraphNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "chunk": self.chunk.to_dict(),
            "score": self.score,
            "graph_nodes": [node.to_dict() for node in self.graph_nodes],
        }
        if self.document is not None:
            payload["document"] = self.document.to_dict()
        return payload


@dataclass
class LearningArtifact:
    id: str
    topic: str
    artifact_type: str
    path: str
    created_at: str
    source_document_ids: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
