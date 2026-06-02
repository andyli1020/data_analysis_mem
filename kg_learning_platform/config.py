from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class ChunkConfig:
    max_chars: int = 900
    overlap_chars: int = 120


@dataclass
class RetrievalConfig:
    top_k: int = 5


@dataclass
class ParserConfig:
    default_backend: str = "basic"
    fallback_to_basic: bool = True


@dataclass
class MinerUConfig:
    enabled: bool = True
    agent_base_url: str = "https://mineru.net/api/v1/agent"
    precision_base_url: str = "https://mineru.net/api/v4"
    language: str = "ch"
    page_range: str = "1-20"
    precision_page_ranges: str = ""
    enable_table: bool = True
    enable_formula: bool = True
    is_ocr: bool = False
    precision_model_version: str = "vlm"
    precision_extra_formats: list[str] = field(default_factory=list)
    precision_no_cache: bool = False
    precision_cache_tolerance: int = 900
    timeout_seconds: float = 30.0
    poll_interval_seconds: float = 3.0
    max_wait_seconds: float = 300.0
    max_upload_mb: float = 10.0
    precision_max_upload_mb: float = 200.0
    precision_api_key_env: str = "MINERU_API_TOKEN"


@dataclass
class LLMConfig:
    provider: str = "none"
    base_url: str = ""
    api_key_env: str = ""
    model: str = ""
    timeout_seconds: float = 90.0


@dataclass
class AppConfig:
    data_root: str = "kg_store"
    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)
    mineru: MinerUConfig = field(default_factory=MinerUConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path or os.getenv("KG_LEARNING_CONFIG", "kg_learning_config.json"))
    payload: Dict[str, Any] = {}
    if config_path.exists():
        payload = json.loads(config_path.read_text(encoding="utf-8"))

    env_payload: Dict[str, Any] = {}
    if os.getenv("KG_LEARNING_DATA_ROOT"):
        env_payload["data_root"] = os.getenv("KG_LEARNING_DATA_ROOT")
    if os.getenv("KG_LEARNING_TOP_K"):
        env_payload.setdefault("retrieval", {})["top_k"] = int(os.getenv("KG_LEARNING_TOP_K", "5"))
    if os.getenv("KG_LEARNING_PARSER_BACKEND"):
        env_payload.setdefault("parser", {})["default_backend"] = os.getenv("KG_LEARNING_PARSER_BACKEND")
    if os.getenv("KG_LEARNING_PARSER_FALLBACK_TO_BASIC"):
        env_payload.setdefault("parser", {})["fallback_to_basic"] = os.getenv(
            "KG_LEARNING_PARSER_FALLBACK_TO_BASIC", "true"
        ).lower() in {"1", "true", "yes", "on"}
    if os.getenv("KG_LEARNING_MINERU_AGENT_BASE_URL"):
        env_payload.setdefault("mineru", {})["agent_base_url"] = os.getenv("KG_LEARNING_MINERU_AGENT_BASE_URL")
    if os.getenv("KG_LEARNING_MINERU_PRECISION_BASE_URL"):
        env_payload.setdefault("mineru", {})["precision_base_url"] = os.getenv("KG_LEARNING_MINERU_PRECISION_BASE_URL")
    if os.getenv("KG_LEARNING_MINERU_LANGUAGE"):
        env_payload.setdefault("mineru", {})["language"] = os.getenv("KG_LEARNING_MINERU_LANGUAGE")
    if os.getenv("KG_LEARNING_MINERU_PAGE_RANGE"):
        env_payload.setdefault("mineru", {})["page_range"] = os.getenv("KG_LEARNING_MINERU_PAGE_RANGE")
    if os.getenv("KG_LEARNING_MINERU_PRECISION_PAGE_RANGES"):
        env_payload.setdefault("mineru", {})["precision_page_ranges"] = os.getenv(
            "KG_LEARNING_MINERU_PRECISION_PAGE_RANGES"
        )
    if os.getenv("KG_LEARNING_MINERU_PRECISION_MODEL_VERSION"):
        env_payload.setdefault("mineru", {})["precision_model_version"] = os.getenv(
            "KG_LEARNING_MINERU_PRECISION_MODEL_VERSION"
        )
    if os.getenv("KG_LEARNING_MINERU_PRECISION_API_KEY_ENV"):
        env_payload.setdefault("mineru", {})["precision_api_key_env"] = os.getenv(
            "KG_LEARNING_MINERU_PRECISION_API_KEY_ENV"
        )
    if os.getenv("KG_LEARNING_MINERU_MAX_WAIT_SECONDS"):
        env_payload.setdefault("mineru", {})["max_wait_seconds"] = float(
            os.getenv("KG_LEARNING_MINERU_MAX_WAIT_SECONDS", "300")
        )
    if os.getenv("KG_LEARNING_LLM_PROVIDER"):
        env_payload.setdefault("llm", {})["provider"] = os.getenv("KG_LEARNING_LLM_PROVIDER")
    if os.getenv("KG_LEARNING_LLM_BASE_URL"):
        env_payload.setdefault("llm", {})["base_url"] = os.getenv("KG_LEARNING_LLM_BASE_URL")
    if os.getenv("KG_LEARNING_LLM_API_KEY_ENV"):
        env_payload.setdefault("llm", {})["api_key_env"] = os.getenv("KG_LEARNING_LLM_API_KEY_ENV")
    if os.getenv("KG_LEARNING_LLM_MODEL"):
        env_payload.setdefault("llm", {})["model"] = os.getenv("KG_LEARNING_LLM_MODEL")

    default = AppConfig().to_dict()
    merged = _merge_dict(_merge_dict(default, payload), env_payload)
    return AppConfig(
        data_root=merged["data_root"],
        chunk=ChunkConfig(**merged.get("chunk", {})),
        retrieval=RetrievalConfig(**merged.get("retrieval", {})),
        parser=ParserConfig(**merged.get("parser", {})),
        mineru=MinerUConfig(**merged.get("mineru", {})),
        llm=LLMConfig(**merged.get("llm", {})),
    )
