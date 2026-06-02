from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .answer import AnswerGenerator
from .chunker import Chunker
from .config import AppConfig, load_config
from .graph import GraphContextBuilder
from .indexer import EmbeddingIndexer, Retriever
from .llm import LLMClient
from .models import Document
from .notebook import NotebookGenerator
from .parser import DocumentParser
from .quality import build_parse_quality_report
from .storage import JsonStorage, utc_now
from .textio import read_text_detected


class LearningPlatform:
    def __init__(self, root: Path | str | None = None, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        if root is not None:
            self.config.data_root = str(root)
        self.storage = JsonStorage(self.config.data_root)
        self.parser = DocumentParser(mineru_config=self.config.mineru)
        self.chunker = Chunker(
            max_chars=self.config.chunk.max_chars,
            overlap_chars=self.config.chunk.overlap_chars,
        )
        self.indexer = EmbeddingIndexer()
        self.graph_builder = GraphContextBuilder()
        self.answer_generator = AnswerGenerator()
        self.llm_client = LLMClient(self.config.llm)
        self.notebook_generator = NotebookGenerator(llm_client=self.llm_client)

    def upload_document(self, source_path: Path | str) -> Document:
        return self.storage.save_uploaded_file(source_path)

    def parse_document(
        self,
        document_id: str,
        backend: str | None = None,
        fallback_to_basic: bool | None = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        document = self.storage.get_document(document_id)
        document_hash = self.storage.file_sha256(document.stored_path)
        document.metadata["file_sha256"] = document_hash
        selected_backend = backend or self.config.parser.default_backend
        allow_fallback = self.config.parser.fallback_to_basic if fallback_to_basic is None else fallback_to_basic
        try:
            try:
                parsed = self._parse_with_cache(
                    document=document,
                    backend=selected_backend,
                    file_sha256=document_hash,
                    force=force,
                )
                parser_backend = selected_backend
                fallback_error = None
            except Exception as exc:
                if selected_backend in {"basic", "local", "local-v1"} or not allow_fallback:
                    raise
                fallback_error = str(exc)
                parsed = self.parser.parse(document.stored_path, backend="basic")
                parser_backend = "basic"
            chunks = self.chunker.split(document.id, str(parsed["text"]))
            quality_report = build_parse_quality_report(str(parsed["text"]), chunk_count=len(chunks))
            document.status = "parsed"
            document.parsed_at = utc_now()
            document.title = str(parsed.get("title") or document.filename)
            document.metadata.update(parsed.get("metadata", {}))
            document.metadata["requested_parser_backend"] = selected_backend
            document.metadata["parser_backend"] = parser_backend
            document.metadata["file_sha256"] = document_hash
            document.metadata["parse_quality"] = quality_report
            if fallback_error:
                document.metadata["parser_fallback_error"] = fallback_error
            else:
                document.metadata.pop("parser_fallback_error", None)
            document.metadata.pop("parse_error", None)
            self.storage.update_document(document)
            self.storage.replace_document_chunks(document.id, chunks)
            self.storage.add_parse_history(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "parsed_at": document.parsed_at,
                    "requested_backend": selected_backend,
                    "parser_backend": parser_backend,
                    "fallback_used": self._backend_id(parser_backend) != self._backend_id(selected_backend),
                    "cache_hit": bool(document.metadata.get("parser_cache_hit")),
                    "chunk_count": len(chunks),
                    "char_count": quality_report["char_count"],
                    "quality_score": quality_report["quality_score"],
                    "formula_count": quality_report["formula_count"],
                    "table_count": quality_report["table_count"],
                    "image_count": quality_report["markdown_image_count"],
                    "error": fallback_error,
                }
            )
            return {
                "document": document.to_dict(),
                "chunk_count": len(chunks),
                "parser_backend": parser_backend,
                "requested_parser_backend": selected_backend,
                "fallback_used": self._backend_id(parser_backend) != self._backend_id(selected_backend),
                "parse_quality": quality_report,
            }
        except Exception as exc:
            document.status = "parse_failed"
            document.parsed_at = utc_now()
            document.metadata["parse_error"] = str(exc)
            document.metadata["requested_parser_backend"] = selected_backend
            document.metadata["file_sha256"] = document_hash
            self.storage.update_document(document)
            raise

    def parser_backends(self) -> List[Dict[str, object]]:
        return self.parser.available_backends()

    def rebuild_index(self) -> Dict[str, Any]:
        chunks = self.storage.list_chunks()
        index_payload = self.indexer.build(chunks)
        self.storage.save_index(index_payload)
        nodes, edges = self.graph_builder.build(chunks)
        self.storage.save_graph(nodes, edges)
        return {
            "chunk_count": len(chunks),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "index_kind": index_payload.get("kind"),
        }

    def reprocess_all(
        self,
        clear_artifacts: bool = False,
        backend: str | None = None,
        fallback_to_basic: bool | None = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        documents = self.storage.list_documents()
        parsed = 0
        skipped = []
        failed = []
        for document in documents:
            selected_backend = backend or self.config.parser.default_backend
            if self._backend_id(selected_backend) in {"mineru", "mineru-precision"} and not self._is_mineru_supported(document):
                skipped.append(
                    {
                        "document_id": document.id,
                        "filename": document.filename,
                        "reason": "unsupported_by_mineru",
                    }
                )
                continue
            try:
                self.parse_document(document.id, backend=backend, fallback_to_basic=fallback_to_basic, force=force)
                parsed += 1
            except Exception as exc:
                failed.append({"document_id": document.id, "filename": document.filename, "error": str(exc)})
        rebuild = self.rebuild_index()
        cleared_artifacts = self.storage.clear_artifacts() if clear_artifacts else 0
        return {
            "document_count": len(documents),
            "parsed_count": parsed,
            "skipped": skipped,
            "failed": failed,
            "cleared_artifacts": cleared_artifacts,
            "rebuild": rebuild,
        }

    def search(self, query: str, top_k: int = 5, document_ids: List[str] | None = None) -> List[Dict[str, Any]]:
        retriever = self._retriever()
        return [result.to_dict() for result in retriever.search(query, top_k=top_k, document_ids=document_ids)]

    def preview_document(self, document_id: str, max_chars: int = 4000) -> Dict[str, Any]:
        document = self.storage.get_document(document_id)
        path = Path(document.stored_path)
        text, encoding = read_text_detected(path)
        return {
            "document": document.to_dict(),
            "encoding": encoding,
            "preview": text[:max_chars],
            "truncated": len(text) > max_chars,
        }

    def list_document_chunks(self, document_id: str, chunk_type: str | None = None) -> List[Dict[str, Any]]:
        self.storage.get_document(document_id)
        chunks = self.storage.list_document_chunks(document_id)
        if chunk_type and chunk_type != "all":
            chunks = [chunk for chunk in chunks if chunk.chunk_type == chunk_type]
        return [chunk.to_dict() for chunk in chunks]

    def document_detail(self, document_id: str) -> Dict[str, Any]:
        document = self.storage.get_document(document_id)
        chunks = self.storage.list_document_chunks(document_id)
        assets = self.storage.list_parsed_assets(document_id)
        history = self.storage.list_parse_history(document_id)[-12:]
        full_md_path = Path(str(document.metadata.get("mineru_full_md_path") or ""))
        full_markdown = ""
        if full_md_path.exists() and full_md_path.is_file():
            full_markdown = full_md_path.read_text(encoding="utf-8", errors="replace")[:12000]
        chunk_type_counts: Dict[str, int] = {}
        for chunk in chunks:
            chunk_type_counts[chunk.chunk_type] = chunk_type_counts.get(chunk.chunk_type, 0) + 1
        return {
            "document": document.to_dict(),
            "chunk_count": len(chunks),
            "chunk_type_counts": chunk_type_counts,
            "assets": assets,
            "history": history,
            "full_markdown_preview": full_markdown,
            "full_markdown_truncated": len(full_markdown) >= 12000,
        }

    def document_asset_path(self, document_id: str, asset_path: str) -> Path:
        self.storage.get_document(document_id)
        return self.storage.resolve_parsed_asset(document_id, asset_path)

    def chat(self, question: str, top_k: int = 5, document_ids: List[str] | None = None) -> Dict[str, Any]:
        results = self._retriever().search(question, top_k=top_k, document_ids=document_ids)
        nodes, edges = self.storage.load_graph()
        graph_context = self.graph_builder.context_for_results([result.chunk.id for result in results], nodes, edges)
        payload = self.answer_generator.answer(question, results)
        payload["graph_context"] = graph_context
        return payload

    def generate_notebook(
        self,
        topic: str,
        source_document_ids: List[str] | None = None,
        difficulty: str = "beginner",
        include_code: bool = True,
        exercise_count: int = 3,
        output_language: str = "zh",
        learning_goal: str = "conceptual",
    ) -> Dict[str, Any]:
        document_ids = source_document_ids or None
        results = self._retriever().search(topic, top_k=8, document_ids=document_ids)
        source_documents = self._source_documents(source_document_ids, results)
        artifact = self.notebook_generator.generate(
            topic=topic,
            results=results,
            source_documents=source_documents,
            output_dir=self.storage.artifacts_dir,
            difficulty=difficulty,
            include_code=include_code,
            exercise_count=exercise_count,
            output_language=output_language,
            learning_goal=learning_goal,
        )
        self.storage.add_artifact(artifact)
        return artifact.to_dict()

    def list_artifacts(self) -> List[Dict[str, Any]]:
        return [artifact.to_dict() for artifact in self.storage.list_artifacts()]

    def health(self) -> Dict[str, Any]:
        documents = self.storage.list_documents()
        chunks = self.storage.list_chunks()
        nodes, edges = self.storage.load_graph()
        return {
            "status": "ok",
            "data_root": str(self.storage.root),
            "documents": len(documents),
            "chunks": len(chunks),
            "graph_nodes": len(nodes),
            "graph_edges": len(edges),
            "llm_enabled": self.llm_client.enabled,
            "config": self.config.to_dict(),
        }

    def delete_artifact(self, artifact_id: str) -> None:
        self.storage.delete_artifact(artifact_id)

    def _retriever(self) -> Retriever:
        nodes, _ = self.storage.load_graph()
        return Retriever(
            index_payload=self.storage.load_index(),
            chunks=self.storage.list_chunks(),
            documents=self.storage.list_documents(),
            nodes=nodes,
        )

    def _parse_with_cache(
        self,
        document: Document,
        backend: str,
        file_sha256: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        backend_id = self._backend_id(backend)
        if backend_id == "mineru-precision":
            artifact_dir = self.storage.document_parsed_dir(document.id, "mineru-precision")
            cached = self._load_cached_mineru_precision(document, artifact_dir, file_sha256, force=force)
            if cached is not None:
                return cached
            parsed = self.parser.parse(document.stored_path, backend=backend, artifact_dir=artifact_dir)
            metadata = dict(parsed.get("metadata", {}))
            metadata.update(
                {
                    "parser_cache_hit": False,
                    "parser_cache_key": file_sha256,
                    "parser_artifact_dir": str(artifact_dir),
                }
            )
            parsed["metadata"] = metadata
            return parsed
        return self.parser.parse(document.stored_path, backend=backend)

    def _load_cached_mineru_precision(
        self,
        document: Document,
        artifact_dir: Path,
        file_sha256: str,
        force: bool = False,
    ) -> Dict[str, Any] | None:
        full_md = artifact_dir / "full.md"
        previous_hash = document.metadata.get("file_sha256")
        previous_backend = self._backend_id(str(document.metadata.get("parser_backend") or document.metadata.get("parser")))
        if force or previous_hash != file_sha256 or previous_backend != "mineru-precision" or not full_md.exists():
            return None
        text = full_md.read_text(encoding="utf-8")
        metadata = {
            "extension": Path(document.stored_path).suffix.lower().lstrip("."),
            "parser": "mineru-precision-api",
            "char_count": len(text),
            "parser_cache_hit": True,
            "parser_cache_key": file_sha256,
            "parser_artifact_dir": str(artifact_dir),
            "mineru_artifact_dir": str(artifact_dir),
            "mineru_full_md_path": str(full_md),
        }
        for key in (
            "mineru_batch_id",
            "mineru_full_zip_url",
            "mineru_zip_path",
            "mineru_image_count",
            "mineru_zip_file_count",
            "mineru_markdown_file",
        ):
            if key in document.metadata:
                metadata[key] = document.metadata[key]
        return {
            "text": text,
            "title": document.title or document.filename,
            "metadata": metadata,
        }

    def _backend_id(self, backend: str | None) -> str:
        aliases = {
            "local": "basic",
            "local-v1": "basic",
            "mineru-agent": "mineru",
            "mineru-agent-api": "mineru",
            "mineru-precision-api": "mineru-precision",
        }
        normalized = (backend or "basic").lower()
        return aliases.get(normalized, normalized)

    def _is_mineru_supported(self, document: Document) -> bool:
        suffix = Path(document.stored_path).suffix.lower()
        return suffix in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"}

    def _source_documents(self, source_document_ids: List[str] | None, results: list) -> List[Document]:
        documents_by_id = {document.id: document for document in self.storage.list_documents()}
        if source_document_ids:
            return [documents_by_id[document_id] for document_id in source_document_ids if document_id in documents_by_id]
        inferred = []
        seen = set()
        for result in results:
            document = result.document
            if document and document.id not in seen:
                inferred.append(document)
                seen.add(document.id)
        return inferred
