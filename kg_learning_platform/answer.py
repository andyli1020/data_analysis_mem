from __future__ import annotations

from typing import List

from .models import SearchResult


class AnswerGenerator:
    """Evidence-first local answer generator.

    A hosted LLM can replace this class later. The local implementation keeps
    V1 useful offline and prevents unsupported claims by summarizing retrieved
    evidence only.
    """

    def answer(self, question: str, results: List[SearchResult]) -> dict:
        if not results:
            return {
                "answer": "我没有在当前知识库中找到足够依据来回答这个问题。请上传相关资料或扩大检索范围。",
                "sources": [],
            }

        lines = [f"问题：{question}", "", "基于当前知识库，最相关的依据如下："]
        for index, result in enumerate(results[:5], start=1):
            source_name = result.document.filename if result.document else result.chunk.document_id
            snippet = self._snippet(result.chunk.text)
            concepts = "、".join(node.label for node in result.graph_nodes[:5])
            concept_part = f"；关联图谱实体：{concepts}" if concepts else ""
            lines.append(f"{index}. {source_name} / {result.chunk.heading}：{snippet}{concept_part}")

        lines.extend(
            [
                "",
                "综合回答：",
                self._synthesize(question, results),
            ]
        )
        return {
            "answer": "\n".join(lines),
            "sources": [result.to_dict() for result in results],
        }

    def _snippet(self, text: str, limit: int = 260) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= limit:
            return normalized
        return normalized[:limit].rstrip() + "..."

    def _synthesize(self, question: str, results: List[SearchResult]) -> str:
        evidence_terms = []
        for result in results:
            for node in result.graph_nodes:
                if node.label not in evidence_terms:
                    evidence_terms.append(node.label)
        if evidence_terms:
            return (
                "这些资料共同指向的核心知识点包括 "
                + "、".join(evidence_terms[:8])
                + "。建议先阅读上面的来源片段，再围绕这些实体查看图谱中的相邻关系。"
            )
        return "建议先阅读上面的来源片段；当前图谱实体不足，后续可通过重建图谱增强关联解释。"
