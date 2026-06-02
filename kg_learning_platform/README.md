# AI Knowledge Graph Learning Platform V1

This is a lightweight local implementation of the architecture plan:

- Modular monolith for local single-user deployment.
- Document parsing, chunking, sparse retrieval, basic evidence graph, chat, and notebook generation.
- GitHub projects are used as architectural references rather than direct forks.
- Phase 1-3 scope now includes health checks, document previews, encoding detection, configurable notebook generation, and a minimal local web UI.

## Reference Mapping

| Area | Reference | V1 implementation |
| --- | --- | --- |
| Document RAG experience | RAGFlow | Local parser + chunk metadata + source-aware answers |
| GraphRAG | Microsoft GraphRAG | Lightweight graph context over retrieved chunks |
| NotebookLM style output | NotebookLlama | Source-driven Jupyter learning notes |
| RAG pipeline modularity | Haystack | Parser / Indexer / Retriever / Generator classes |
| Vector store | Qdrant / FAISS | Local sparse TF-IDF abstraction, swappable later |
| Notebook file format | Jupyter nbformat | Standards-compliant `.ipynb` JSON generation |

## CLI Quickstart

```powershell
& 'C:\Users\Andyl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m kg_learning_platform.cli --root kg_store upload .\papers\literature_notes.md
& 'C:\Users\Andyl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m kg_learning_platform.cli --root kg_store parse <document_id>
& 'C:\Users\Andyl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m kg_learning_platform.cli --root kg_store rebuild
& 'C:\Users\Andyl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m kg_learning_platform.cli --root kg_store search "Transformer Attention"
& 'C:\Users\Andyl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m kg_learning_platform.cli --root kg_store notebook "Transformer"
```

## API Server

Install optional server dependencies first:

```powershell
pip install fastapi uvicorn python-multipart
```

Then run:

```powershell
uvicorn kg_learning_platform.api:app --reload
```

Endpoints implemented:

- `GET /api/health`
- `GET /api/parser/backends`
- `POST /api/documents/upload`
- `POST /api/documents/{id}/parse`
- `GET /api/documents/{id}/preview`
- `GET /api/documents/{id}/chunks`
- `POST /api/index/rebuild`
- `GET /api/search`
- `POST /api/chat`
- `POST /api/learning-artifacts/generate-notebook`
- `GET /api/learning-artifacts`
- `GET /api/learning-artifacts/{id}/download`
- `DELETE /api/learning-artifacts/{id}`

The minimal web UI is served from:

- `http://127.0.0.1:8765/`
- API docs: `http://127.0.0.1:8765/docs`

Notebook generation supports:

- `difficulty`: `beginner` or `intermediate`
- `learning_goal`: `conceptual`, `practice`, or `review`
- `output_language`: default `zh`
- `include_code`
- `exercise_count`

## Configuration

Copy `kg_learning_config.example.json` to `kg_learning_config.json` to customize local settings.
Environment variables can override key values:

- `KG_LEARNING_DATA_ROOT`
- `KG_LEARNING_TOP_K`
- `KG_LEARNING_PARSER_BACKEND`
- `KG_LEARNING_PARSER_FALLBACK_TO_BASIC`
- `KG_LEARNING_MINERU_AGENT_BASE_URL`
- `KG_LEARNING_MINERU_LANGUAGE`
- `KG_LEARNING_MINERU_PAGE_RANGE`
- `KG_LEARNING_MINERU_MAX_WAIT_SECONDS`
- `KG_LEARNING_LLM_PROVIDER`
- `KG_LEARNING_LLM_BASE_URL`
- `KG_LEARNING_LLM_API_KEY_ENV`
- `KG_LEARNING_LLM_MODEL`

## MinerU API Parser

V1 can call MinerU Agent API as an optional parser backend for formula-heavy
courseware PDFs. It also supports MinerU precision API with token auth and VLM
parsing. The local parser remains the default and MinerU failures can fall back
to local parsing.

Parse one document with MinerU:

```powershell
& '.\.venv\Scripts\python.exe' -m kg_learning_platform.cli --root kg_store parse <document_id> --backend mineru
```

Parse one document with MinerU precision API:

```powershell
$env:MINERU_API_TOKEN = "<your-token>"
& '.\.venv\Scripts\python.exe' -m kg_learning_platform.cli --root kg_store parse <document_id> --backend mineru-precision
```

Or via API:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8765/api/documents/<document_id>/parse" `
  -ContentType "application/json" `
  -Body '{"backend":"mineru-precision","fallback_to_basic":true}'
```

The web UI exposes `本地解析`, `MinerU 解析`, and `MinerU 精准解析` on each
document card.

## V2 Upgrade Points

- Replace local sparse index with FAISS or Qdrant.
- Replace JSON graph with Neo4j.
- Promote MinerU precision API or Docling/RAGFlow-style document understanding for complex PDFs.
- Add hosted LLM generation for richer chat and notebook sections.
