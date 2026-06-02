from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List
from urllib import request

from .config import LLMConfig


@dataclass
class LLMClient:
    config: LLMConfig

    @property
    def enabled(self) -> bool:
        return (
            self.config.provider != "none"
            and bool(self.config.base_url)
            and bool(self.config.model)
            and bool(self.api_key)
        )

    @property
    def api_key(self) -> str:
        return os.getenv(self.config.api_key_env, "") if self.config.api_key_env else ""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.enabled:
            return ""
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions",
            data=data,
            headers=self._headers(),
            method="POST",
        )
        with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    def _headers(self) -> Dict[str, str]:
        if self.config.provider.lower() == "mimo":
            return {"Content-Type": "application/json", "api-key": self.api_key}
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}


NOTEBOOK_SYSTEM_PROMPT = """你是一个面向 AI 论文和大学课件的学习材料生成助手。
你的任务是把检索到的资料组织成清晰、循序渐进、适合 Jupyter Notebook 的中文学习笔记。
不要编造资料中没有的事实；如果依据不足，请用学习提示或问题引导替代确定性结论。"""


def build_notebook_section_prompt(topic: str, section_title: str, evidence: str, difficulty: str) -> str:
    return f"""主题：{topic}
小节标题：{section_title}
学习难度：{difficulty}

请基于以下资料片段写一个 Notebook Markdown 小节，包含：
1. 核心解释
2. 为什么重要
3. 一个帮助理解的小例子
4. 1 个自检问题

资料片段：
{evidence}
"""
