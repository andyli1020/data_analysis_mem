from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

try:
    from fastapi import FastAPI, File, HTTPException, Query, UploadFile
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - exercised only when server deps are missing.
    raise RuntimeError(
        "FastAPI API requires optional dependencies. Install fastapi, uvicorn, and python-multipart."
    ) from exc

from .pipeline import LearningPlatform
from .config import load_config


platform = LearningPlatform(config=load_config())
app = FastAPI(title="AI Knowledge Graph Learning Platform", version="0.1.0")


class RebuildResponse(BaseModel):
    chunk_count: int
    node_count: int
    edge_count: int
    index_kind: str


class ChatRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = None


class NotebookRequest(BaseModel):
    topic: str
    source_document_ids: List[str] = Field(default_factory=list)
    difficulty: str = "beginner"
    include_code: bool = True
    exercise_count: int = Field(default=3, ge=1, le=10)
    output_format: str = "ipynb"
    output_language: str = "zh"
    learning_goal: str = "conceptual"


class ReprocessRequest(BaseModel):
    clear_artifacts: bool = False
    backend: Optional[str] = None
    fallback_to_basic: Optional[bool] = None
    force: bool = False


class ParseRequest(BaseModel):
    backend: Optional[str] = None
    fallback_to_basic: Optional[bool] = None
    force: bool = False


@app.get("/api/health")
def health() -> dict:
    return platform.health()


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    document = platform.storage.save_upload_bytes(data, file.filename or "upload.bin", file.content_type or "")
    return document.to_dict()


@app.post("/api/documents/{document_id}/parse")
def parse_document(
    document_id: str,
    request: ParseRequest | None = None,
    backend: Optional[str] = Query(default=None),
    fallback_to_basic: Optional[bool] = Query(default=None),
    force: Optional[bool] = Query(default=None),
) -> dict:
    try:
        body = request or ParseRequest()
        selected_backend = backend if backend is not None else body.backend
        selected_fallback = fallback_to_basic if fallback_to_basic is not None else body.fallback_to_basic
        selected_force = force if force is not None else body.force
        return platform.parse_document(
            document_id,
            backend=selected_backend,
            fallback_to_basic=selected_fallback,
            force=selected_force,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/parser/backends")
def parser_backends() -> list:
    return platform.parser_backends()


@app.get("/api/documents")
def list_documents() -> list:
    return [document.to_dict() for document in platform.storage.list_documents()]


@app.get("/api/documents/{document_id}/preview")
def preview_document(document_id: str, max_chars: int = Query(default=4000, ge=1, le=20000)) -> dict:
    try:
        return platform.preview_document(document_id, max_chars=max_chars)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/documents/{document_id}/detail")
def document_detail(document_id: str) -> dict:
    try:
        return platform.document_detail(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/documents/{document_id}/chunks")
def list_document_chunks(document_id: str, chunk_type: Optional[str] = Query(default=None)) -> list:
    try:
        return platform.list_document_chunks(document_id, chunk_type=chunk_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/documents/{document_id}/assets/{asset_path:path}")
def get_document_asset(document_id: str, asset_path: str) -> FileResponse:
    try:
        path = platform.document_asset_path(document_id, asset_path)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(path, filename=path.name)


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str) -> dict:
    platform.storage.delete_document(document_id)
    return {"ok": True}


@app.post("/api/index/rebuild", response_model=RebuildResponse)
def rebuild_index() -> dict:
    return platform.rebuild_index()


@app.post("/api/maintenance/reprocess-all")
def reprocess_all(request: ReprocessRequest) -> dict:
    return platform.reprocess_all(
        clear_artifacts=request.clear_artifacts,
        backend=request.backend,
        fallback_to_basic=request.fallback_to_basic,
        force=request.force,
    )


@app.get("/api/search")
def search(q: str = Query(..., min_length=1), top_k: int = Query(default=5, ge=1, le=20)) -> list:
    return platform.search(q, top_k=top_k)


@app.get("/api/graph")
def graph() -> dict:
    nodes, edges = platform.storage.load_graph()
    return {
        "nodes": [node.to_dict() for node in nodes],
        "edges": [edge.to_dict() for edge in edges],
    }


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    return platform.chat(request.question, top_k=request.top_k, document_ids=request.document_ids)


@app.post("/api/learning-artifacts/generate-notebook")
def generate_notebook(request: NotebookRequest) -> dict:
    if request.output_format != "ipynb":
        raise HTTPException(status_code=400, detail="V1 only supports output_format='ipynb'.")
    return platform.generate_notebook(
        topic=request.topic,
        source_document_ids=request.source_document_ids,
        difficulty=request.difficulty,
        include_code=request.include_code,
        exercise_count=request.exercise_count,
        output_language=request.output_language,
        learning_goal=request.learning_goal,
    )


@app.get("/api/learning-artifacts")
def list_learning_artifacts() -> list:
    return platform.list_artifacts()


@app.get("/api/learning-artifacts/{artifact_id}")
def get_learning_artifact(artifact_id: str) -> dict:
    try:
        return platform.storage.get_artifact(artifact_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/learning-artifacts/{artifact_id}/download")
def download_learning_artifact(artifact_id: str) -> FileResponse:
    try:
        artifact = platform.storage.get_artifact(artifact_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    path = Path(artifact.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact file is missing.")
    return FileResponse(path, filename=path.name, media_type="application/x-ipynb+json")


@app.delete("/api/learning-artifacts/{artifact_id}")
def delete_learning_artifact(artifact_id: str) -> dict:
    platform.delete_artifact(artifact_id)
    return {"ok": True}


WEB_DIR = Path(__file__).parent / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
