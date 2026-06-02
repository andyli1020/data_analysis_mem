from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List

from .models import Chunk, Document, GraphNode, SearchResult


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+\-.]{1,}|[\u4e00-\u9fff]{2,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "have",
    "has",
    "into",
    "using",
    "based",
    "一个",
    "我们",
    "可以",
    "以及",
    "进行",
}


def tokenize(text: str) -> List[str]:
    tokens = [match.group(0).lower() for match in TOKEN_RE.finditer(text)]
    cjk_tokens: List[str] = []
    for token in tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 2:
            cjk_tokens.extend(token[index : index + 2] for index in range(len(token) - 1))
            cjk_tokens.append(token)
        else:
            cjk_tokens.append(token)
    return [token for token in cjk_tokens if token not in STOPWORDS and len(token) > 1]


class EmbeddingIndexer:
    """Sparse local vector index.

    This is a FAISS-compatible conceptual placeholder for V1: the rest of the
    system talks to an indexer/retriever abstraction, so Qdrant/FAISS can replace
    it later without changing API handlers or notebook generation.
    """

    def build(self, chunks: Iterable[Chunk]) -> Dict[str, object]:
        chunk_vectors: Dict[str, Dict[str, float]] = {}
        document_frequency: Counter[str] = Counter()
        chunk_list = list(chunks)
        raw_counts: Dict[str, Counter[str]] = {}
        for chunk in chunk_list:
            counts = Counter(tokenize(chunk.text))
            raw_counts[chunk.id] = counts
            document_frequency.update(counts.keys())

        chunk_count = max(1, len(chunk_list))
        idf = {
            token: math.log((1 + chunk_count) / (1 + frequency)) + 1.0
            for token, frequency in document_frequency.items()
        }
        for chunk_id, counts in raw_counts.items():
            weighted = {token: count * idf[token] for token, count in counts.items()}
            norm = math.sqrt(sum(value * value for value in weighted.values())) or 1.0
            chunk_vectors[chunk_id] = {token: value / norm for token, value in weighted.items()}

        return {
            "version": 1,
            "kind": "local-sparse-tfidf",
            "idf": idf,
            "vectors": chunk_vectors,
        }


class Retriever:
    def __init__(self, index_payload: Dict[str, object], chunks: List[Chunk], documents: List[Document], nodes: List[GraphNode] | None = None) -> None:
        self.index_payload = index_payload or {}
        self.chunks = {chunk.id: chunk for chunk in chunks}
        self.documents = {document.id: document for document in documents}
        self.nodes = nodes or []
        self.chunk_to_nodes: Dict[str, List[GraphNode]] = {}
        for node in self.nodes:
            for chunk_id in node.source_chunk_ids:
                self.chunk_to_nodes.setdefault(chunk_id, []).append(node)

    def search(self, query: str, top_k: int = 5, document_ids: List[str] | None = None) -> List[SearchResult]:
        idf = self.index_payload.get("idf", {})
        vectors = self.index_payload.get("vectors", {})
        if not isinstance(idf, dict) or not isinstance(vectors, dict):
            return []
        query_counts = Counter(tokenize(query))
        query_weighted = {
            token: count * float(idf.get(token, 1.0))
            for token, count in query_counts.items()
        }
        query_norm = math.sqrt(sum(value * value for value in query_weighted.values())) or 1.0
        query_vector = {token: value / query_norm for token, value in query_weighted.items()}

        allowed = set(document_ids or [])
        scored: List[SearchResult] = []
        query_lower = query.lower()
        for chunk_id, vector in vectors.items():
            chunk = self.chunks.get(chunk_id)
            if chunk is None:
                continue
            if allowed and chunk.document_id not in allowed:
                continue
            if not isinstance(vector, dict):
                continue
            score = sum(query_vector.get(token, 0.0) * float(value) for token, value in vector.items())
            if query_lower and query_lower in chunk.text.lower():
                score += 0.15
            if score <= 0:
                continue
            scored.append(
                SearchResult(
                    chunk=chunk,
                    score=round(score, 6),
                    document=self.documents.get(chunk.document_id),
                    graph_nodes=self.chunk_to_nodes.get(chunk.id, [])[:8],
                )
            )
        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:top_k]
