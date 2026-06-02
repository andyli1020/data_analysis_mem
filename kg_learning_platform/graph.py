from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple

from .indexer import tokenize
from .models import Chunk, GraphEdge, GraphNode


DOMAIN_TERMS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Neural Network",
    "CNN",
    "RNN",
    "Transformer",
    "Attention",
    "BERT",
    "GPT",
    "Large Language Model",
    "LLM",
    "Diffusion Model",
    "GAN",
    "ViT",
    "Dataset",
    "Metric",
    "Accuracy",
    "F1",
    "Precision",
    "Recall",
    "NumPy",
    "Pandas",
    "DataFrame",
    "PCA",
    "StandardScaler",
    "MinMaxScaler",
]

TECH_PHRASE_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z0-9+.-]{1,}(?:\s+[A-Z][A-Za-z0-9+.-]{1,}){0,3}|[A-Z]{2,}[A-Za-z0-9+.-]*)\b"
)


def canonical_label(label: str) -> str:
    label = re.sub(r"\s+", " ", label.strip(" .,;:()[]{}"))
    aliases = {
        "large language models": "Large Language Model",
        "large language model": "Large Language Model",
        "llms": "LLM",
        "dataframe": "DataFrame",
        "diffusion models": "Diffusion Model",
        "transformers": "Transformer",
    }
    return aliases.get(label.lower(), label)


def node_id(label: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "_", label.lower()).strip("_")
    return f"ent_{normalized[:80]}" or "ent_unknown"


def infer_type(label: str) -> str:
    lower = label.lower()
    if any(marker in lower for marker in ["dataset", "mnist", "imagenet", "cifar", "wine", "iris"]):
        return "Dataset"
    if any(marker in lower for marker in ["accuracy", "f1", "precision", "recall", "metric"]):
        return "Metric"
    if any(marker in lower for marker in ["model", "bert", "gpt", "cnn", "gan", "transformer", "vit", "llm"]):
        return "Model"
    if any(marker in lower for marker in ["classification", "detection", "segmentation", "prediction"]):
        return "Task"
    if any(marker in lower for marker in ["pandas", "numpy", "scaler", "pca"]):
        return "Method"
    return "Concept"


class GraphContextBuilder:
    def extract_entities(self, text: str) -> List[str]:
        found: Counter[str] = Counter()
        lower_text = text.lower()
        for term in DOMAIN_TERMS:
            if term.lower() in lower_text:
                found[canonical_label(term)] += 3
        for match in TECH_PHRASE_RE.finditer(text):
            label = canonical_label(match.group(0))
            if len(label) < 2 or label.lower() in {"the", "this", "figure", "table"}:
                continue
            found[label] += 1
        for token in tokenize(text):
            if token in {"transformer", "attention", "embedding", "dataset", "pandas", "numpy"}:
                found[canonical_label(token.title())] += 1
        return [label for label, _ in found.most_common(12)]

    def build(self, chunks: Iterable[Chunk]) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes: Dict[str, GraphNode] = {}
        chunk_entities: Dict[str, List[str]] = {}
        for chunk in chunks:
            labels = self.extract_entities(chunk.text)
            chunk_entities[chunk.id] = labels
            for label in labels:
                entity_id = node_id(label)
                node = nodes.get(entity_id)
                if node is None:
                    node = GraphNode(
                        id=entity_id,
                        label=label,
                        type=infer_type(label),
                    )
                    nodes[entity_id] = node
                node.mentions += 1
                if chunk.id not in node.source_chunk_ids:
                    node.source_chunk_ids.append(chunk.id)

        edge_map: Dict[tuple[str, str, str], GraphEdge] = {}
        for chunk_id, labels in chunk_entities.items():
            unique_ids = [node_id(label) for label in labels if node_id(label) in nodes]
            for entity_id in unique_ids:
                key = (chunk_id, entity_id, "CHUNK_MENTIONS_CONCEPT")
                edge_map[key] = GraphEdge(source=chunk_id, target=entity_id, type="CHUNK_MENTIONS_CONCEPT", evidence_chunk_ids=[chunk_id])
            for left, right in self._co_occurring_pairs(unique_ids):
                edge_type = self._infer_relation(nodes[left], nodes[right])
                key = (left, right, edge_type)
                edge = edge_map.get(key)
                if edge is None:
                    edge = GraphEdge(source=left, target=right, type=edge_type, evidence_chunk_ids=[])
                    edge_map[key] = edge
                if chunk_id not in edge.evidence_chunk_ids:
                    edge.evidence_chunk_ids.append(chunk_id)
        return list(nodes.values()), list(edge_map.values())

    def context_for_results(self, result_chunk_ids: List[str], nodes: List[GraphNode], edges: List[GraphEdge]) -> Dict[str, object]:
        node_by_id = {node.id: node for node in nodes}
        chunk_set = set(result_chunk_ids)
        relevant_node_ids = {
            node.id
            for node in nodes
            if any(chunk_id in chunk_set for chunk_id in node.source_chunk_ids)
        }
        relevant_edges = [
            edge
            for edge in edges
            if edge.source in relevant_node_ids and edge.target in relevant_node_ids
        ]
        return {
            "nodes": [node_by_id[node_id].to_dict() for node_id in sorted(relevant_node_ids) if node_id in node_by_id],
            "edges": [edge.to_dict() for edge in relevant_edges],
        }

    def _co_occurring_pairs(self, entity_ids: List[str]) -> List[tuple[str, str]]:
        pairs = []
        for left_index, left in enumerate(entity_ids):
            for right in entity_ids[left_index + 1 : left_index + 5]:
                if left != right:
                    pairs.append((left, right))
        return pairs

    def _infer_relation(self, left: GraphNode, right: GraphNode) -> str:
        if left.type == "Concept" and right.type == "Concept":
            return "CONCEPT_RELATED_TO_CONCEPT"
        if left.type in {"Method", "Model"} and right.type == "Task":
            return "METHOD_SOLVES_TASK"
        if left.type in {"Method", "Model"} and right.type == "Dataset":
            return "METHOD_USES_DATASET"
        if left.type in {"Method", "Model"} and right.type == "Metric":
            return "METHOD_EVALUATED_BY_METRIC"
        return "RELATED_TO"
