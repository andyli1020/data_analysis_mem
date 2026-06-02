from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Protocol

from .models import Document, LearningArtifact, SearchResult
from .storage import new_id, utc_now
from .llm import NOTEBOOK_SYSTEM_PROMPT, build_notebook_section_prompt


class SupportsComplete(Protocol):
    @property
    def enabled(self) -> bool: ...

    def complete(self, system_prompt: str, user_prompt: str) -> str: ...


def markdown_cell(source: str) -> Dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip() + "\n"}


def code_cell(source: str) -> Dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip() + "\n",
    }


class NotebookGenerator:
    def __init__(self, style_dir: Path | str = "ref", llm_client: SupportsComplete | None = None) -> None:
        self.style_dir = Path(style_dir)
        self.llm_client = llm_client
        self.style_profile = self._load_style_profile(self.style_dir)

    def generate(
        self,
        topic: str,
        results: List[SearchResult],
        source_documents: List[Document],
        output_dir: Path,
        difficulty: str = "beginner",
        include_code: bool = True,
        exercise_count: int = 3,
        output_language: str = "zh",
        learning_goal: str = "conceptual",
    ) -> LearningArtifact:
        artifact_id = new_id("artifact")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{artifact_id}_{self._slug(topic)}.ipynb"
        notebook_path = output_dir / filename
        notebook = self._build_notebook(
            topic=topic,
            results=results,
            source_documents=source_documents,
            difficulty=difficulty,
            include_code=include_code,
            exercise_count=exercise_count,
            output_language=output_language,
            learning_goal=learning_goal,
        )
        self._validate_notebook(notebook)
        notebook_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
        return LearningArtifact(
            id=artifact_id,
            topic=topic,
            artifact_type="jupyter_notebook",
            path=str(notebook_path),
            created_at=utc_now(),
            source_document_ids=[document.id for document in source_documents],
            parameters={
                "difficulty": difficulty,
                "include_code": include_code,
                "exercise_count": exercise_count,
                "output_format": "ipynb",
                "output_language": output_language,
                "learning_goal": learning_goal,
                "style_profile": self.style_profile,
            },
        )

    def _build_notebook(
        self,
        topic: str,
        results: List[SearchResult],
        source_documents: List[Document],
        difficulty: str,
        include_code: bool,
        exercise_count: int,
        output_language: str,
        learning_goal: str,
    ) -> Dict[str, object]:
        concepts = self._concepts(results)
        source_names = [document.filename for document in source_documents]
        objectives = self._objectives(topic, concepts, difficulty)
        outline = self._build_outline(topic, concepts, results, learning_goal)
        cells: List[Dict[str, object]] = [
            markdown_cell(
                f"""# {topic} 学习笔记

本 Notebook 基于本地知识库资料自动生成，目标是把论文、课件和笔记整理成可快速复习、可继续实验的学习材料。

生成风格参考了本项目 `ref` 目录中的学习 Notebook：先给路线，再讲概念，然后用代码和练习巩固。

## 学习目标

{objectives}

## 使用资料

{self._bullet_list(source_names or ["当前检索结果"])}
"""
            )
        ]

        cells.append(
            markdown_cell(
                f"""## 1. 学习路线与先修知识

建议按以下顺序学习：

1. 先把 `{topic}` 的基本定义和问题背景读清楚。
2. 再理解关键概念之间的关系：{", ".join(concepts[:6]) if concepts else "概念、方法、数据和评价指标"}。
3. 然后结合代码或小例子验证自己的理解。
4. 最后用练习题检查是否能迁移到新资料。

建议先具备：

{self._prerequisites(topic, concepts, difficulty)}
"""
            )
        )

        cells.append(
            markdown_cell(
                f"""## 2. 核心概念速览

{self._concept_overview(topic, concepts)}
"""
            )
        )

        for offset, result in enumerate(results[:4], start=0):
            section_index = offset + 3
            title = outline[offset] if offset < len(outline) else result.graph_nodes[0].label if result.graph_nodes else result.chunk.heading or f"材料片段 {offset + 1}"
            cells.append(
                markdown_cell(
                    f"""## {section_index}. {title}

{self._section_markdown(result, topic, title, difficulty)}

**资料片段**

> {self._quote(result.chunk.text)}
"""
                )
            )
            if include_code and offset == 0:
                cells.append(code_cell(self._code_example(topic, concepts)))

        cells.append(
            markdown_cell(
                f"""## 练习

{self._exercises(topic, concepts, exercise_count)}
"""
            )
        )

        cells.append(
            markdown_cell(
                f"""## 参考来源

{self._source_section(results, source_documents)}
"""
            )
        )

        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "pygments_lexer": "ipython3",
                },
                "kg_learning_platform": {
                    "generator": "NotebookGenerator",
                    "citation_mode": "weak",
                    "difficulty": difficulty,
                    "output_language": output_language,
                    "learning_goal": learning_goal,
                },
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    def _validate_notebook(self, notebook: Dict[str, object]) -> None:
        if notebook.get("nbformat") != 4:
            raise ValueError("Notebook nbformat must be 4.")
        cells = notebook.get("cells")
        if not isinstance(cells, list) or not cells:
            raise ValueError("Notebook must contain cells.")
        for cell in cells:
            if not isinstance(cell, dict) or cell.get("cell_type") not in {"markdown", "code"}:
                raise ValueError("Invalid notebook cell.")
            if cell.get("cell_type") == "code":
                source = str(cell.get("source", ""))
                ast.parse(source)

    def _concepts(self, results: Iterable[SearchResult]) -> List[str]:
        concepts: List[str] = []
        for result in results:
            for node in result.graph_nodes:
                if node.label not in concepts:
                    concepts.append(node.label)
        return concepts[:10]

    def _objectives(self, topic: str, concepts: List[str], difficulty: str) -> str:
        goals = [
            f"理解 `{topic}` 的核心问题、基本定义和典型应用场景。",
            "能够把资料中的关键概念整理成自己的知识结构。",
            "能够通过一个小型代码示例验证学习内容。",
        ]
        if difficulty == "intermediate":
            goals.append("能够比较不同方法、数据集或评价指标之间的差异。")
        if concepts:
            goals.append("重点关注：" + "、".join(concepts[:6]) + "。")
        return self._bullet_list(goals)

    def _build_outline(self, topic: str, concepts: List[str], results: List[SearchResult], learning_goal: str) -> List[str]:
        if concepts:
            outline = [f"理解 {concept}" for concept in concepts[:4]]
        else:
            outline = [result.chunk.heading for result in results[:4] if result.chunk.heading]
        if learning_goal == "practice":
            outline = [f"{item}：实践视角" for item in outline]
        elif learning_goal == "review":
            outline = [f"{item}：复习要点" for item in outline]
        return outline[:4] or [f"{topic} 的核心问题", f"{topic} 的关键概念"]

    def _prerequisites(self, topic: str, concepts: List[str], difficulty: str) -> str:
        items = ["能阅读基本的课程讲义或论文摘要", "愿意边读边整理概念关系"]
        if difficulty == "intermediate":
            items.extend(["了解基础机器学习术语", "能运行简单 Python 代码"])
        if any(item in " ".join(concepts) for item in ["NumPy", "Pandas", "PCA"]):
            items.append("熟悉 Python 数据分析基础")
        return self._bullet_list(items)

    def _concept_overview(self, topic: str, concepts: List[str]) -> str:
        if not concepts:
            return f"当前资料中尚未抽取到稳定概念。建议先围绕 `{topic}` 阅读来源片段，再手动补充术语表。"
        lines = []
        for concept in concepts[:8]:
            lines.append(f"- **{concept}**：与 `{topic}` 相关的关键节点，后续可以在图谱中继续查看其来源和相邻关系。")
        return "\n".join(lines)

    def _section_markdown(self, result: SearchResult, topic: str, title: str, difficulty: str) -> str:
        evidence = self._quote(result.chunk.text, limit=1200)
        if self.llm_client and self.llm_client.enabled:
            generated = self.llm_client.complete(
                NOTEBOOK_SYSTEM_PROMPT,
                build_notebook_section_prompt(topic, title, evidence, difficulty),
            )
            if generated:
                return generated
        return self._teaching_explanation(result, topic)

    def _teaching_explanation(self, result: SearchResult, topic: str) -> str:
        concepts = [node.label for node in result.graph_nodes[:5]]
        source = result.document.filename if result.document else "知识库资料"
        concept_text = "、".join(concepts) if concepts else topic
        return (
            f"这一节来自 `{source}`，适合用来理解 `{topic}` 中的 `{concept_text}`。"
            "阅读时不要只记住名词，要关注它解决什么问题、依赖哪些前置知识，以及它和其他方法的关系。"
        )

    def _code_example(self, topic: str, concepts: List[str]) -> str:
        concept_items = concepts[:6] or [topic, "Concept", "Evidence"]
        return f"""
concepts = {concept_items!r}

print("本节关键概念：")
for i, concept in enumerate(concepts, start=1):
    print(f"{{i}}. {{concept}}")

knowledge_map = {{
    "topic": {topic!r},
    "concepts": concepts,
    "review_prompt": "请用自己的话解释每个概念，并写出它和主题的关系。"
}}

knowledge_map
"""

    def _exercises(self, topic: str, concepts: List[str], count: int) -> str:
        base = [
            f"用 3-5 句话解释 `{topic}` 的核心思想。",
            "从参考资料中找出一个关键概念，说明它的输入、输出和适用场景。",
            "画一个小型概念图，把主题、方法、数据集和评价指标连接起来。",
            "选择两个相关方法，比较它们的相同点、差异和可能的使用场景。",
            "把本 Notebook 的代码示例改成你自己的主题词列表。",
        ]
        if concepts:
            base.insert(1, f"解释 `{concepts[0]}` 与 `{topic}` 的关系。")
        selected = base[: max(1, count)]
        return "\n".join(f"{index}. {item}" for index, item in enumerate(selected, start=1))

    def _source_section(self, results: List[SearchResult], documents: List[Document]) -> str:
        seen = set()
        lines = []
        for document in documents:
            seen.add(document.id)
            lines.append(f"- {document.filename}")
        for result in results:
            if result.document and result.document.id not in seen:
                seen.add(result.document.id)
                lines.append(f"- {result.document.filename}")
        return "\n".join(lines) if lines else "- 当前知识库检索结果"

    def _quote(self, text: str, limit: int = 420) -> str:
        normalized = " ".join(text.split())
        if len(normalized) > limit:
            normalized = normalized[:limit].rstrip() + "..."
        return normalized.replace("\n", " ")

    def _bullet_list(self, items: Iterable[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    def _slug(self, text: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "_", text).strip("_")
        return slug[:48] or "learning_note"

    def _load_style_profile(self, style_dir: Path) -> Dict[str, object]:
        notebooks = sorted(style_dir.glob("*.ipynb"))
        profile = {
            "sample_count": len(notebooks),
            "preferred_format": "jupyter",
            "common_sections": ["学习目标", "学习路线", "核心概念", "代码示例", "练习", "参考来源"],
            "uses_code_cells": True,
        }
        if not notebooks:
            return profile
        markdown_cells = 0
        code_cells = 0
        headings: List[str] = []
        for path in notebooks:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for cell in payload.get("cells", []):
                source = "".join(cell.get("source", []))
                if cell.get("cell_type") == "markdown":
                    markdown_cells += 1
                    headings.extend(re.findall(r"^#{1,3}\s+(.+)$", source, flags=re.MULTILINE))
                elif cell.get("cell_type") == "code":
                    code_cells += 1
        profile.update(
            {
                "markdown_cells": markdown_cells,
                "code_cells": code_cells,
                "observed_headings": headings[:12],
            }
        )
        return profile
