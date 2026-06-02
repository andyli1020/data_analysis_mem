#!/usr/bin/env python
"""
Translate markdown chunks into Chinese using an OpenAI-compatible chat API.

Supported providers:
- OpenAI-compatible API
- DeepSeek API (OpenAI-compatible format)
- MiMo API (Xiaomi)

Environment variables:
    OPENAI_API_KEY       Optional for provider=openai
    OPENAI_BASE_URL      Optional. Defaults to https://api.openai.com/v1
    OPENAI_MODEL         Optional. Can be overridden by --model
    DEEPSEEK_API_KEY     Optional for provider=deepseek
    DEEPSEEK_BASE_URL    Optional. Defaults to https://api.deepseek.com
    DEEPSEEK_MODEL       Optional. Defaults to deepseek-v4-flash
    MIMO_API_KEY         Optional for provider=mimo
    MIMO_BASE_URL        Optional. Defaults to https://token-plan-cn.xiaomimimo.com/v1
    MIMO_MODEL           Optional. Defaults to mimo-v2.5-pro

Examples:
    python 04_translate.py \
        --manifest work/chunks/generative_ai_labor_demand/manifest.json \
        --output-dir work/translated/generative_ai_labor_demand \
        --provider deepseek

    python 04_translate.py \
        --manifest work/chunks/generative_ai_labor_demand/manifest.json \
        --output-dir work/translated/generative_ai_labor_demand \
        --provider mimo
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import requests
from requests import RequestException


SYSTEM_PROMPT = """You are an academic translation assistant.
Translate English academic prose into clear, faithful Chinese suitable for deep reading.

Rules:
1. Preserve argument structure, hedging, causal relations, comparisons, and numeric content.
2. Keep paragraph structure unless the input is visibly broken.
3. Use glossary terms when provided.
4. Do not invent content.
5. Output translation only. Do not add notes, summaries, term lists, headings, or commentary unless they already appear in the source.
"""

PROVIDER_CONFIG = {
    "openai": {
        "base_url_env": "OPENAI_BASE_URL",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4.1-mini",
        "auth_style": "bearer",
    },
    "deepseek": {
        "base_url_env": "DEEPSEEK_BASE_URL",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
        "default_base_url": "https://api.deepseek.com",
        "default_model": "deepseek-v4-flash",
        "auth_style": "bearer",
    },
    "mimo": {
        "base_url_env": "MIMO_BASE_URL",
        "api_key_env": "MIMO_API_KEY",
        "model_env": "MIMO_MODEL",
        "default_base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "auth_style": "api-key",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Chunk manifest JSON.")
    parser.add_argument("--glossary", type=Path, help="Optional glossary JSON used only for term consistency.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Translated chunk directory.")
    parser.add_argument(
        "--provider",
        choices=sorted(PROVIDER_CONFIG.keys()),
        default="openai",
        help="API provider name.",
    )
    parser.add_argument("--model", help="Override model name.")
    parser.add_argument("--base-url", help="Override provider base URL.")
    parser.add_argument("--api-key", help="Override API key.")
    parser.add_argument("--target-language", default="中文")
    parser.add_argument("--sleep-seconds", type=float, default=0.3)
    parser.add_argument("--timeout-seconds", type=float, default=180)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--retry-wait-seconds", type=float, default=3.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        help="Translate only the first N chunks from the manifest.",
    )
    return parser.parse_args()


def load_json(path: Path | None) -> Dict:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def format_glossary(glossary_data: Dict, max_entries: int = 40) -> str:
    entries = glossary_data.get("entries", [])
    lines: List[str] = []
    for entry in entries[:max_entries]:
        source = entry.get("source_term", "").strip()
        translation = entry.get("translation", "").strip()
        if not source:
            continue
        if translation:
            lines.append(f"- {source}: {translation}")
        else:
            lines.append(f"- {source}: [待定]")
    return "\n".join(lines)


def build_user_prompt(chunk_text: str, glossary_text: str, target_language: str) -> str:
    glossary_block = ""
    if glossary_text:
        glossary_block = f"术语参考（如适用请尽量统一，但不要额外输出术语表）：\n{glossary_text}\n\n"
    return f"""请将以下英文论文内容翻译为适合{target_language}深度阅读的学术译文。

要求：
1. 只输出译文本身，不要添加“本段术语”“本段要点”“可能需人工复核”等任何额外结构。
2. 不要额外补标题；只有当原文片段中本来就有标题时，才翻译并保留其层级。
3. 保留段落分隔、列表、表格标题、图题等原有结构。
4. 术语尽量保持前后一致。

{glossary_block}待翻译内容：
```markdown
{chunk_text}
```
"""


def resolve_provider_settings(args: argparse.Namespace) -> tuple[str, str, str, str, str]:
    config = PROVIDER_CONFIG[args.provider]
    base_url = args.base_url or os.getenv(config["base_url_env"], config["default_base_url"])
    api_key = args.api_key or os.getenv(config["api_key_env"], "")
    model = args.model or os.getenv(config["model_env"], config["default_model"])
    auth_style = config["auth_style"]
    return args.provider, base_url, api_key, model, auth_style


def call_chat_api(
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: float,
    auth_style: str = "bearer",
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    if auth_style == "api-key":
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def write_translation(output_path: Path, content: str, metadata: Dict[str, object]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "---",
        f'chunk_id: "{metadata["chunk_id"]}"',
        f'title: "{str(metadata["title"]).replace("\"", "\\\"")}"',
        f'model: "{str(metadata["model"]).replace("\"", "\\\"")}"',
        f'source_file: "{str(metadata["source_file"]).replace("\\", "/")}"',
        "---",
        "",
    ]
    output_path.write_text("\n".join(header) + content.strip() + "\n", encoding="utf-8")


def translate_with_retries(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: float,
    max_retries: int,
    retry_wait_seconds: float,
    chunk_name: str,
    auth_style: str = "bearer",
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return call_chat_api(
                base_url=base_url,
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                timeout_seconds=timeout_seconds,
                auth_style=auth_style,
            )
        except RequestException as exc:
            last_error = exc
            if attempt >= max_retries:
                break
            print(
                f"Retry {attempt}/{max_retries - 1} for {chunk_name} after error: "
                f"{exc.__class__.__name__}"
            )
            time.sleep(retry_wait_seconds)
    assert last_error is not None
    raise last_error


def main() -> None:
    args = parse_args()
    provider, base_url, api_key, model, auth_style = resolve_provider_settings(args)
    if not args.dry_run and not api_key:
        config = PROVIDER_CONFIG[provider]
        raise SystemExit(f'{config["api_key_env"]} is required unless --dry-run is used.')

    manifest = load_json(args.manifest)
    glossary_data = load_json(args.glossary)
    glossary_text = format_glossary(glossary_data)

    chunks = manifest.get("chunks", [])
    if args.limit is not None:
        chunks = chunks[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for item in chunks:
        source_path = Path(item["source_file"])
        output_name = source_path.name.replace(".md", ".zh.md")
        output_path = args.output_dir / output_name
        if output_path.exists() and not args.overwrite:
            print(f"Skip existing: {output_path.name}")
            continue

        chunk_text = source_path.read_text(encoding="utf-8")
        user_prompt = build_user_prompt(chunk_text, glossary_text, args.target_language)

        if args.dry_run:
            translated = "这是一个 dry-run 占位结果。请在配置 API 后执行真实翻译。\n"
        else:
            translated = translate_with_retries(
                base_url=base_url,
                api_key=api_key,
                model=model,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                timeout_seconds=args.timeout_seconds,
                max_retries=args.max_retries,
                retry_wait_seconds=args.retry_wait_seconds,
                chunk_name=output_name,
                auth_style=auth_style,
            )
            time.sleep(args.sleep_seconds)

        write_translation(
            output_path,
            translated,
            metadata={
                "chunk_id": item["chunk_id"],
                "title": item["title"],
                "model": model,
                "source_file": item["source_file"],
            },
        )
        print(f"Translated: {output_path.name}")


if __name__ == "__main__":
    main()
