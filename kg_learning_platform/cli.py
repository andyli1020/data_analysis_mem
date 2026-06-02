from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import LearningPlatform


def main() -> None:
    parser = argparse.ArgumentParser(description="Local AI knowledge graph learning platform CLI.")
    parser.add_argument("--root", default="kg_store", help="Local data root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload = subparsers.add_parser("upload", help="Upload a local document into the store.")
    upload.add_argument("path", type=Path)

    parse = subparsers.add_parser("parse", help="Parse a document by id.")
    parse.add_argument("document_id")
    parse.add_argument("--backend", choices=["basic", "mineru", "mineru-precision"], default=None)
    parse.add_argument("--no-fallback", action="store_true")
    parse.add_argument("--force", action="store_true", help="Ignore cached parser artifacts.")

    subparsers.add_parser("rebuild", help="Rebuild sparse index and graph.")

    search = subparsers.add_parser("search", help="Search the knowledge base.")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)

    chat = subparsers.add_parser("chat", help="Ask an evidence-first question.")
    chat.add_argument("question")
    chat.add_argument("--top-k", type=int, default=5)

    notebook = subparsers.add_parser("notebook", help="Generate a learning notebook.")
    notebook.add_argument("topic")
    notebook.add_argument("--difficulty", choices=["beginner", "intermediate"], default="beginner")
    notebook.add_argument("--learning-goal", choices=["conceptual", "practice", "review"], default="conceptual")
    notebook.add_argument("--output-language", default="zh")
    notebook.add_argument("--no-code", action="store_true")
    notebook.add_argument("--exercise-count", type=int, default=3)

    args = parser.parse_args()
    platform = LearningPlatform(args.root)

    if args.command == "upload":
        payload = platform.upload_document(args.path).to_dict()
    elif args.command == "parse":
        payload = platform.parse_document(
            args.document_id,
            backend=args.backend,
            fallback_to_basic=not args.no_fallback,
            force=args.force,
        )
    elif args.command == "rebuild":
        payload = platform.rebuild_index()
    elif args.command == "search":
        payload = platform.search(args.query, top_k=args.top_k)
    elif args.command == "chat":
        payload = platform.chat(args.question, top_k=args.top_k)
    elif args.command == "notebook":
        payload = platform.generate_notebook(
            args.topic,
            difficulty=args.difficulty,
            include_code=not args.no_code,
            exercise_count=args.exercise_count,
            output_language=args.output_language,
            learning_goal=args.learning_goal,
        )
    else:
        raise AssertionError(args.command)

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
