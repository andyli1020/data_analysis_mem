from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

from kg_learning_platform import LearningPlatform
from kg_learning_platform.api import app, platform
from kg_learning_platform.chunker import Chunker
from kg_learning_platform.config import AppConfig
from kg_learning_platform.mineru import MinerUClient, MinerUError
from kg_learning_platform.parser import DocumentParser


class FakeMinerUClient:
    def parse_file_agent(self, path: Path | str) -> dict:
        return {
            "text": "# 感知机课件\n\n线性分类器公式：$y = sign(w^T x + b)$\n\n| 符号 | 含义 |\n| --- | --- |",
            "title": "感知机课件",
            "metadata": {
                "parser": "mineru-agent-api",
                "mineru_task_id": "task_mock",
            },
        }


class FakePrecisionMinerUClient:
    calls = 0

    def parse_file_precision(self, path: Path | str, artifact_dir: Path | str | None = None) -> dict:
        self.calls += 1
        artifact_path = Path(artifact_dir) if artifact_dir is not None else Path(path).parent.parent / "parsed" / "mock"
        artifact_path.mkdir(parents=True, exist_ok=True)
        (artifact_path / "full.md").write_text(
            "# 精准解析课件\n\nVLM 公式结果：$\\nabla_w L(w)$\n\n## 表格\n\n| A | B |\n| --- | --- |",
            encoding="utf-8",
        )
        return {
            "text": "# 精准解析课件\n\nVLM 公式结果：$\\nabla_w L(w)$\n\n## 表格\n\n| A | B |\n| --- | --- |",
            "title": "精准解析课件",
            "metadata": {
                "parser": "mineru-precision-api",
                "mineru_batch_id": "batch_mock",
                "parser_artifact_dir": str(artifact_path),
            },
        }


class FailingMinerUClient:
    def parse_file_agent(self, path: Path | str) -> dict:
        raise MinerUError("mock mineru outage")


class LearningPlatformTests(unittest.TestCase):
    def test_end_to_end_learning_notebook(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "transformer_note.md"
            source.write_text(
                """# Transformer 入门

Transformer 是一种基于 Attention 的深度学习模型，常用于自然语言处理和大语言模型。

## 核心概念

Attention 机制用于建模序列中不同 token 之间的关系。BERT 和 GPT 都与 Transformer 架构有关。

## 数据与评价

模型通常会在 Dataset 上训练，并使用 Accuracy、F1、Precision 和 Recall 等 Metric 评价。
""",
                encoding="utf-8",
            )

            platform = LearningPlatform(tmp_path / "store")
            document = platform.upload_document(source)
            parsed = platform.parse_document(document.id)
            self.assertGreaterEqual(parsed["chunk_count"], 1)
            self.assertEqual(parsed["document"]["metadata"]["encoding"], "utf-8")

            preview = platform.preview_document(document.id)
            self.assertIn("Transformer 入门", preview["preview"])

            chunks = platform.list_document_chunks(document.id)
            self.assertGreaterEqual(len(chunks), 1)

            rebuild = platform.rebuild_index()
            self.assertGreaterEqual(rebuild["chunk_count"], 1)
            self.assertGreaterEqual(rebuild["node_count"], 1)

            results = platform.search("Transformer Attention GPT", top_k=3)
            self.assertTrue(results)
            self.assertEqual(results[0]["document"]["filename"], "transformer_note.md")

            answer = platform.chat("Transformer 和 Attention 有什么关系？")
            self.assertTrue("来源" in answer["answer"] or "依据" in answer["answer"])
            self.assertTrue(answer["sources"])
            self.assertTrue(answer["graph_context"]["nodes"])

            health = platform.health()
            self.assertEqual(health["status"], "ok")
            self.assertGreaterEqual(health["documents"], 1)

            artifact = platform.generate_notebook(
                "Transformer",
                include_code=True,
                exercise_count=3,
                output_language="zh",
                learning_goal="review",
            )
            notebook_path = Path(artifact["path"])
            self.assertTrue(notebook_path.exists())
            notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
            self.assertEqual(notebook["nbformat"], 4)
            cell_types = [cell["cell_type"] for cell in notebook["cells"]]
            self.assertIn("markdown", cell_types)
            self.assertIn("code", cell_types)
            joined = "\n".join(cell["source"] for cell in notebook["cells"])
            self.assertIn("# Transformer 学习笔记", joined)
            self.assertIn("## 练习", joined)
            self.assertIn("## 参考来源", joined)
            self.assertIn("## 1. 学习路线与先修知识", joined)
            self.assertIn("## 2. 核心概念速览", joined)
            self.assertEqual(notebook["metadata"]["kg_learning_platform"]["learning_goal"], "review")

            repaired = platform.reprocess_all(clear_artifacts=True)
            self.assertEqual(repaired["parsed_count"], 1)
            self.assertEqual(repaired["cleared_artifacts"], 1)
            clean_chunks = platform.list_document_chunks(document.id)
            self.assertEqual(clean_chunks[0]["heading"], "Transformer 入门")
            self.assertIn("Attention", clean_chunks[0]["text"])
            self.assertNotIn("��", clean_chunks[0]["text"])
            self.assertNotIn("锟", clean_chunks[0]["text"])

    def test_gb18030_markdown_is_decoded_for_preview_and_parse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "gb_note.md"
            source.write_bytes("# 中文标题\n\n机器学习可以辅助学习。".encode("gb18030"))
            platform = LearningPlatform(tmp_path / "store")
            document = platform.upload_document(source)
            parsed = platform.parse_document(document.id)
            self.assertEqual(parsed["document"]["metadata"]["encoding"], "gb18030")
            preview = platform.preview_document(document.id)
            self.assertIn("中文标题", preview["preview"])

    def test_mineru_parser_backend_can_be_injected_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "lecture.pdf"
            source.write_bytes(b"%PDF-1.4 mock")
            platform = LearningPlatform(tmp_path / "store")
            platform.parser = DocumentParser(
                mineru_config=platform.config.mineru,
                mineru_client=FakeMinerUClient(),
            )
            document = platform.upload_document(source)
            parsed = platform.parse_document(document.id, backend="mineru", fallback_to_basic=False)
            self.assertEqual(parsed["parser_backend"], "mineru")
            self.assertFalse(parsed["fallback_used"])
            self.assertGreaterEqual(parsed["chunk_count"], 1)
            self.assertEqual(parsed["document"]["metadata"]["parser"], "mineru-agent-api")
            self.assertEqual(parsed["document"]["metadata"]["mineru_task_id"], "task_mock")
            chunks = platform.list_document_chunks(document.id)
            self.assertIn("$y = sign", chunks[0]["text"])

    def test_mineru_precision_parser_backend_can_be_injected_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "formula_lecture.pdf"
            source.write_bytes(b"%PDF-1.4 mock")
            platform = LearningPlatform(tmp_path / "store")
            platform.parser = DocumentParser(
                mineru_config=platform.config.mineru,
                mineru_client=FakePrecisionMinerUClient(),
            )
            document = platform.upload_document(source)
            parsed = platform.parse_document(document.id, backend="mineru-precision", fallback_to_basic=False)
            self.assertEqual(parsed["parser_backend"], "mineru-precision")
            self.assertFalse(parsed["fallback_used"])
            self.assertGreaterEqual(parsed["chunk_count"], 1)
            self.assertEqual(parsed["document"]["metadata"]["parser"], "mineru-precision-api")
            self.assertEqual(parsed["document"]["metadata"]["mineru_batch_id"], "batch_mock")
            self.assertGreaterEqual(parsed["parse_quality"]["formula_count"], 1)
            self.assertGreaterEqual(parsed["parse_quality"]["table_count"], 1)
            chunks = platform.list_document_chunks(document.id)
            self.assertIn("\\nabla_w", chunks[0]["text"])
            detail = platform.document_detail(document.id)
            self.assertIn("formula", detail["chunk_type_counts"])
            self.assertTrue(any(asset["relative_path"] == "mineru-precision/full.md" for asset in detail["assets"]))
            formula_chunks = platform.list_document_chunks(document.id, chunk_type="formula")
            self.assertTrue(formula_chunks)
            self.assertTrue(all(chunk["chunk_type"] == "formula" for chunk in formula_chunks))
            asset_path = platform.document_asset_path(document.id, "mineru-precision/full.md")
            self.assertTrue(asset_path.exists())
            with self.assertRaises(ValueError):
                platform.document_asset_path(document.id, "../metadata/documents.json")

    def test_mineru_precision_cache_reuses_local_full_md(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "cached_lecture.pdf"
            source.write_bytes(b"%PDF-1.4 mock")
            client = FakePrecisionMinerUClient()
            platform = LearningPlatform(tmp_path / "store")
            platform.parser = DocumentParser(
                mineru_config=platform.config.mineru,
                mineru_client=client,
            )
            document = platform.upload_document(source)
            artifact_dir = platform.storage.document_parsed_dir(document.id, "mineru-precision")
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "full.md").write_text("# Cached\n\n公式 $w^T x$。", encoding="utf-8")
            document = platform.storage.get_document(document.id)
            document.metadata["file_sha256"] = platform.storage.file_sha256(document.stored_path)
            document.metadata["parser_backend"] = "mineru-precision"
            platform.storage.update_document(document)

            parsed = platform.parse_document(document.id, backend="mineru-precision", fallback_to_basic=False)
            self.assertEqual(client.calls, 0)
            self.assertTrue(parsed["document"]["metadata"]["parser_cache_hit"])
            self.assertIn("$w^T x$", platform.list_document_chunks(document.id)[0]["text"])

    def test_mineru_zip_is_saved_and_full_markdown_is_rewritten(self) -> None:
        class Response:
            status_code = 200
            text = ""

            def __init__(self, content: bytes) -> None:
                self.content = content

        class Session:
            def __init__(self, content: bytes) -> None:
                self.content = content

            def get(self, url: str, timeout: float) -> Response:
                return Response(self.content)

        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as archive:
                archive.writestr("result/full.md", "# Title\n\n![](images/a.png)\n\n公式 $x+y$")
                archive.writestr("result/images/a.png", b"png")
            client = MinerUClient(session=Session(zip_buffer.getvalue()))
            artifact_dir = tmp_path / "artifact"
            payload = client._download_markdown_from_zip("https://example.test/result.zip", artifact_dir=artifact_dir)
            self.assertTrue((artifact_dir / "mineru_result.zip").exists())
            self.assertTrue((artifact_dir / "full.md").exists())
            self.assertTrue((artifact_dir / "result" / "images" / "a.png").exists())
            self.assertIn("result/images/a.png", payload["text"])
            self.assertEqual(payload["mineru_image_count"], 1)

    def test_mineru_backend_falls_back_to_basic_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "fallback_note.md"
            source.write_text("# Fallback\n\nBasic parser should still work.", encoding="utf-8")
            config = AppConfig()
            config.parser.fallback_to_basic = True
            platform = LearningPlatform(tmp_path / "store", config=config)
            platform.parser = DocumentParser(
                mineru_config=platform.config.mineru,
                mineru_client=FailingMinerUClient(),
            )
            document = platform.upload_document(source)
            parsed = platform.parse_document(document.id, backend="mineru")
            self.assertEqual(parsed["parser_backend"], "basic")
            self.assertTrue(parsed["fallback_used"])
            self.assertIn("mock mineru outage", parsed["document"]["metadata"]["parser_fallback_error"])

    def test_web_assets_exist(self) -> None:
        web_dir = Path("kg_learning_platform/web")
        self.assertTrue((web_dir / "index.html").exists())
        self.assertTrue((web_dir / "app.js").exists())
        self.assertTrue((web_dir / "styles.css").exists())

    def test_chunker_preserves_structured_blocks(self) -> None:
        html_table = "<table>" + "".join(f"<tr><td>{index}</td><td>{index * index}</td></tr>" for index in range(80)) + "</table>"
        formula = "$$\n" + " + ".join(f"x_{index}" for index in range(120)) + "\n$$"
        text = f"# Structured\n\nIntro paragraph.\n\n{html_table}\n\n{formula}\n\nTail paragraph."
        chunks = Chunker(max_chars=180, overlap_chars=20).split("doc_structured", text)
        table_chunks = [chunk for chunk in chunks if chunk.chunk_type == "table"]
        formula_chunks = [chunk for chunk in chunks if chunk.chunk_type == "formula"]
        self.assertEqual(len(table_chunks), 1)
        self.assertTrue(table_chunks[0].text.startswith("<table>"))
        self.assertTrue(table_chunks[0].text.endswith("</table>"))
        self.assertEqual(len(formula_chunks), 1)
        self.assertTrue(formula_chunks[0].text.startswith("$$"))
        self.assertTrue(formula_chunks[0].text.endswith("$$"))

    def test_api_routes_are_registered_for_phase_1_to_3(self) -> None:
        routes = {getattr(route, "path", "") for route in app.routes}
        expected = {
            "/api/health",
            "/api/documents/upload",
            "/api/documents/{document_id}/parse",
            "/api/parser/backends",
            "/api/documents/{document_id}/preview",
            "/api/documents/{document_id}/detail",
            "/api/documents/{document_id}/chunks",
            "/api/documents/{document_id}/assets/{asset_path:path}",
            "/api/index/rebuild",
            "/api/maintenance/reprocess-all",
            "/api/search",
            "/api/graph",
            "/api/chat",
            "/api/learning-artifacts/generate-notebook",
            "/api/learning-artifacts/{artifact_id}/download",
            "",
        }
        self.assertTrue(expected.issubset(routes))
        self.assertEqual(platform.health()["status"], "ok")

    def test_reference_notebooks_have_target_style(self) -> None:
        ref_dir = Path("ref")
        notebooks = sorted(ref_dir.glob("*.ipynb"))
        self.assertTrue(notebooks, "ref notebooks should exist as style references")
        for path in notebooks:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("nbformat"), 4)
            self.assertTrue(
                any(cell.get("cell_type") == "markdown" for cell in payload.get("cells", []))
            )


if __name__ == "__main__":
    unittest.main()
