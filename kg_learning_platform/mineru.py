from __future__ import annotations

import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib.parse import urljoin
import re

import requests

from .config import MinerUConfig


class MinerUError(RuntimeError):
    """Raised when MinerU API parsing fails."""


class MinerUClient:
    """Small client for MinerU Agent lightweight parsing API.

    The API flow is asynchronous:
    1. Request an upload URL for the file.
    2. Upload the file bytes to that URL.
    3. Poll the extraction task.
    4. Download the Markdown result URL.
    """

    def __init__(self, config: MinerUConfig | None = None, session: requests.Session | None = None) -> None:
        self.config = config or MinerUConfig()
        self.session = session or requests.Session()

    def parse_file(self, path: Path | str) -> Dict[str, Any]:
        return self.parse_file_agent(path)

    def parse_file_agent(self, path: Path | str) -> Dict[str, Any]:
        file_path = Path(path)
        if not file_path.exists():
            raise MinerUError(f"File not found: {file_path}")
        if file_path.stat().st_size > self.config.max_upload_mb * 1024 * 1024:
            raise MinerUError(
                f"MinerU Agent API is configured for files up to {self.config.max_upload_mb:g} MB: {file_path.name}"
            )

        submit_payload = self._submit_file(file_path)
        task_id = self._first_value(
            submit_payload,
            keys=("task_id", "taskId", "id", "batch_id", "batchId"),
        )
        if not task_id:
            raise MinerUError(f"MinerU did not return a task id: {submit_payload}")

        result_payload = self._poll_task(str(task_id))
        markdown_url = self._find_markdown_url(result_payload)
        markdown = self._download_markdown(markdown_url) if markdown_url else self._find_markdown_text(result_payload)
        if not markdown or not markdown.strip():
            raise MinerUError(f"MinerU completed but no Markdown result was found: {result_payload}")

        return {
            "text": markdown,
            "title": file_path.stem,
            "metadata": {
                "parser": "mineru-agent-api",
                "mineru_task_id": str(task_id),
                "mineru_markdown_url": markdown_url,
                "mineru_result": self._compact_payload(result_payload),
            },
        }

    def parse_file_precision(
        self,
        path: Path | str,
        api_key: str | None = None,
        artifact_dir: Path | str | None = None,
    ) -> Dict[str, Any]:
        file_path = Path(path)
        token = api_key or self._api_token()
        if not token:
            raise MinerUError(
                f"MinerU precision parser requires an API token in {self.config.precision_api_key_env}."
            )
        if not file_path.exists():
            raise MinerUError(f"File not found: {file_path}")
        if file_path.stat().st_size > self.config.precision_max_upload_mb * 1024 * 1024:
            raise MinerUError(
                "MinerU precision API is configured for files up to "
                f"{self.config.precision_max_upload_mb:g} MB: {file_path.name}"
            )

        create_payload = self._precision_post_json(
            "file-urls/batch",
            self._precision_file_payload(file_path),
            token=token,
        )
        batch_id = self._first_value(create_payload, ("batch_id", "batchId"))
        file_url = self._first_value(create_payload, ("file_url", "fileUrl"))
        if not file_url:
            file_urls = self._first_value(create_payload, ("file_urls", "fileUrls"))
            if isinstance(file_urls, list) and file_urls:
                file_url = file_urls[0]
        if not batch_id or not file_url:
            raise MinerUError(f"MinerU precision API did not return batch_id and file_url: {create_payload}")

        with file_path.open("rb") as handle:
            response = self.session.put(str(file_url), data=handle, timeout=self.config.timeout_seconds)
        if response.status_code >= 400:
            raise MinerUError(f"MinerU precision upload failed ({response.status_code}): {response.text[:500]}")

        result_payload = self._poll_precision_batch(str(batch_id), token=token)
        file_result = self._pick_precision_file_result(result_payload, file_path.name)
        full_zip_url = self._first_value(file_result, ("full_zip_url", "fullZipUrl"))
        if not full_zip_url:
            full_zip_url = self._find_url(file_result, hints=("full_zip", "fullzip", "zip"))
        if not full_zip_url:
            raise MinerUError(f"MinerU precision completed but no full_zip_url was found: {file_result}")

        markdown_payload = self._download_markdown_from_zip(str(full_zip_url), artifact_dir=artifact_dir)
        markdown = markdown_payload["text"]
        if not markdown.strip():
            raise MinerUError(f"MinerU precision zip did not contain Markdown text: {full_zip_url}")

        asset_metadata = {
            key: value
            for key, value in markdown_payload.items()
            if key != "text"
        }
        return {
            "text": markdown,
            "title": file_path.stem,
            "metadata": {
                "parser": "mineru-precision-api",
                "mineru_batch_id": str(batch_id),
                "mineru_full_zip_url": str(full_zip_url),
                **asset_metadata,
                "mineru_result": self._compact_payload(file_result),
            },
        }

    def _submit_file(self, file_path: Path) -> Dict[str, Any]:
        payload = {
            "file_name": file_path.name,
            "language": self.config.language,
            "page_range": self.config.page_range,
            "enable_table": self.config.enable_table,
            "enable_formula": self.config.enable_formula,
            "is_ocr": self.config.is_ocr,
        }
        create_payload = self._post_json("parse/file", payload)
        upload_url = self._first_value(
            create_payload,
            keys=("file_url", "fileUrl", "upload_url", "uploadUrl", "url", "presigned_url", "presignedUrl"),
        )
        if not upload_url:
            upload_url = self._find_url(create_payload, hints=("upload", "put"))
        if not upload_url:
            raise MinerUError(f"MinerU did not return an upload URL: {create_payload}")

        with file_path.open("rb") as handle:
            response = self.session.put(str(upload_url), data=handle, timeout=self.config.timeout_seconds)
        if response.status_code >= 400:
            raise MinerUError(f"MinerU upload failed ({response.status_code}): {response.text[:500]}")

        return create_payload

    def _poll_task(self, task_id: str) -> Dict[str, Any]:
        deadline = time.monotonic() + self.config.max_wait_seconds
        last_payload: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            payload = self._get_json(f"parse/{task_id}")
            last_payload = payload
            status = str(self._first_value(payload, ("status", "state", "task_status", "taskStatus")) or "").lower()
            if status in {"done", "success", "succeeded", "completed", "finish", "finished"}:
                return payload
            if status in {"failed", "fail", "error", "canceled", "cancelled"}:
                raise MinerUError(f"MinerU task failed: {payload}")
            if self._find_markdown_url(payload) or self._find_markdown_text(payload):
                return payload
            time.sleep(self.config.poll_interval_seconds)
        raise MinerUError(f"MinerU task timed out after {self.config.max_wait_seconds:g}s: {last_payload}")

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.post(self._url(path), json=payload, timeout=self.config.timeout_seconds)
        return self._json_response(response)

    def _get_json(self, path: str) -> Dict[str, Any]:
        response = self.session.get(self._url(path), timeout=self.config.timeout_seconds)
        return self._json_response(response)

    def _download_markdown(self, url: str) -> str:
        response = self.session.get(url, timeout=self.config.timeout_seconds)
        if response.status_code >= 400:
            raise MinerUError(f"MinerU Markdown download failed ({response.status_code}): {response.text[:500]}")
        response.encoding = response.encoding or "utf-8"
        return response.text

    def _download_markdown_from_zip(self, url: str, artifact_dir: Path | str | None = None) -> Dict[str, Any]:
        response = self.session.get(url, timeout=self.config.timeout_seconds)
        if response.status_code >= 400:
            raise MinerUError(f"MinerU zip download failed ({response.status_code}): {response.text[:500]}")
        zip_bytes = response.content
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            names = archive.namelist()
            preferred = [
                name
                for name in names
                if name.lower().endswith("full.md") or name.lower().endswith("/full.md")
            ]
            markdown_names = preferred or [name for name in names if name.lower().endswith(".md")]
            if not markdown_names:
                raise MinerUError(f"MinerU zip did not include a Markdown file: {names}")
            markdown_name = markdown_names[0]
            markdown = archive.read(markdown_name).decode("utf-8", errors="replace")
            metadata: Dict[str, Any] = {
                "mineru_zip_file_count": len(names),
                "mineru_markdown_file": markdown_name,
            }
            if artifact_dir is not None:
                target = Path(artifact_dir)
                self._safe_extract_zip(zip_bytes, target)
                zip_path = target / "mineru_result.zip"
                zip_path.write_bytes(zip_bytes)
                source_md_path = target / markdown_name
                full_md_path = target / "full.md"
                if source_md_path.exists() and source_md_path != full_md_path:
                    full_md_path.write_text(markdown, encoding="utf-8")
                rewritten = self._rewrite_markdown_asset_paths(markdown, markdown_name)
                full_md_path.write_text(rewritten, encoding="utf-8")
                markdown = rewritten
                image_count = len([name for name in names if self._is_image_name(name)])
                metadata.update(
                    {
                        "mineru_artifact_dir": str(target),
                        "mineru_zip_path": str(zip_path),
                        "mineru_full_md_path": str(full_md_path),
                        "mineru_image_count": image_count,
                    }
                )
            return {"text": markdown, **metadata}

    def _safe_extract_zip(self, zip_bytes: bytes, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)
        target_root = target.resolve()
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            for member in archive.infolist():
                member_path = (target / member.filename).resolve()
                if not str(member_path).startswith(str(target_root)):
                    raise MinerUError(f"Unsafe path in MinerU zip: {member.filename}")
            archive.extractall(target)

    def _rewrite_markdown_asset_paths(self, markdown: str, markdown_name: str) -> str:
        markdown_dir = Path(markdown_name).parent
        if str(markdown_dir) == ".":
            markdown_dir = Path("")

        def replace(match: re.Match[str]) -> str:
            alt_text = match.group(1)
            asset_path = match.group(2).strip()
            if asset_path.startswith(("http://", "https://", "/", "#", "data:")):
                return match.group(0)
            local_path = (markdown_dir / asset_path).as_posix()
            return f"![{alt_text}]({local_path})"

        return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, markdown)

    def _is_image_name(self, name: str) -> bool:
        return Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}

    def _json_response(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            raise MinerUError(f"MinerU API failed ({response.status_code}): {response.text[:500]}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise MinerUError(f"MinerU API returned non-JSON response: {response.text[:500]}") from exc
        if isinstance(payload, dict) and str(payload.get("code", "0")) not in {"0", "200", "success"}:
            message = payload.get("msg") or payload.get("message") or payload
            raise MinerUError(f"MinerU API returned an error: {message}")
        return payload if isinstance(payload, dict) else {"data": payload}

    def _precision_post_json(self, path: str, payload: Dict[str, Any], token: str) -> Dict[str, Any]:
        response = self.session.post(
            self._precision_url(path),
            json=payload,
            headers=self._precision_headers(token),
            timeout=self.config.timeout_seconds,
        )
        return self._json_response(response)

    def _precision_get_json(self, path: str, token: str) -> Dict[str, Any]:
        response = self.session.get(
            self._precision_url(path),
            headers=self._precision_headers(token),
            timeout=self.config.timeout_seconds,
        )
        return self._json_response(response)

    def _url(self, path: str) -> str:
        base = self.config.agent_base_url.rstrip("/") + "/"
        return urljoin(base, path.lstrip("/"))

    def _precision_url(self, path: str) -> str:
        base = self.config.precision_base_url.rstrip("/") + "/"
        return urljoin(base, path.lstrip("/"))

    def _precision_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _precision_file_payload(self, file_path: Path) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "enable_formula": self.config.enable_formula,
            "enable_table": self.config.enable_table,
            "language": self.config.language,
            "files": [
                {
                    "name": file_path.name,
                    "is_ocr": self.config.is_ocr,
                    "data_id": file_path.stem,
                }
            ],
        }
        if self.config.precision_model_version:
            payload["model_version"] = self.config.precision_model_version
        if self.config.precision_extra_formats:
            payload["extra_formats"] = self.config.precision_extra_formats
        if self.config.precision_no_cache:
            payload["no_cache"] = self.config.precision_no_cache
        if self.config.precision_cache_tolerance:
            payload["cache_tolerance"] = self.config.precision_cache_tolerance
        if self.config.precision_page_ranges:
            payload["files"][0]["page_ranges"] = self.config.precision_page_ranges
        return payload

    def _poll_precision_batch(self, batch_id: str, token: str) -> Dict[str, Any]:
        deadline = time.monotonic() + self.config.max_wait_seconds
        last_payload: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            payload = self._precision_get_json(f"extract-results/batch/{batch_id}", token=token)
            last_payload = payload
            file_result = self._pick_precision_file_result(payload, "")
            state = str(
                self._first_value(file_result or payload, ("state", "status", "task_status", "taskStatus")) or ""
            ).lower()
            if state in {"done", "success", "succeeded", "completed", "finish", "finished"}:
                return payload
            if state in {"failed", "fail", "error", "canceled", "cancelled"}:
                raise MinerUError(f"MinerU precision task failed: {payload}")
            if self._find_url(payload, hints=("full_zip", "fullzip", "zip")):
                return payload
            time.sleep(self.config.poll_interval_seconds)
        raise MinerUError(f"MinerU precision task timed out after {self.config.max_wait_seconds:g}s: {last_payload}")

    def _pick_precision_file_result(self, payload: Dict[str, Any], filename: str) -> Dict[str, Any]:
        candidates = []
        for value in self._walk_values(payload):
            if isinstance(value, dict) and (
                self._first_value(value, ("full_zip_url", "fullZipUrl"))
                or self._first_value(value, ("state", "status"))
            ):
                candidates.append(value)
        if not candidates:
            return payload
        if filename:
            for candidate in candidates:
                name = str(self._first_value(candidate, ("file_name", "fileName", "name")) or "")
                if name == filename:
                    return candidate
        return candidates[0]

    def _api_token(self) -> str:
        import os

        return os.getenv(self.config.precision_api_key_env, "").strip()

    def _find_markdown_url(self, payload: Dict[str, Any]) -> str | None:
        return self._find_url(payload, hints=("markdown", "md", "result"))

    def _find_markdown_text(self, payload: Dict[str, Any]) -> str | None:
        for value in self._walk_values(payload):
            if isinstance(value, str) and self._looks_like_markdown(value):
                return value
        return None

    def _find_url(self, payload: Dict[str, Any], hints: Iterable[str]) -> str | None:
        lowered_hints = tuple(hint.lower() for hint in hints)
        stack: list[tuple[str, Any]] = [("", payload)]
        while stack:
            key, value = stack.pop()
            if isinstance(value, dict):
                stack.extend((str(child_key), child_value) for child_key, child_value in value.items())
            elif isinstance(value, list):
                stack.extend((key, item) for item in value)
            elif isinstance(value, str) and value.startswith(("http://", "https://")):
                lower_key = key.lower()
                lower_value = value.lower()
                if any(hint in lower_key or hint in lower_value for hint in lowered_hints):
                    return value
        return None

    def _first_value(self, payload: Dict[str, Any], keys: Iterable[str]) -> Any:
        wanted = set(keys)
        for key, value in self._walk_items(payload):
            if key in wanted and value not in (None, ""):
                return value
        return None

    def _walk_items(self, value: Any) -> Iterable[tuple[str, Any]]:
        if isinstance(value, dict):
            for key, item in value.items():
                yield str(key), item
                yield from self._walk_items(item)
        elif isinstance(value, list):
            for item in value:
                yield from self._walk_items(item)

    def _walk_values(self, value: Any) -> Iterable[Any]:
        if isinstance(value, dict):
            for item in value.values():
                yield item
                yield from self._walk_values(item)
        elif isinstance(value, list):
            for item in value:
                yield item
                yield from self._walk_values(item)

    def _looks_like_markdown(self, value: str) -> bool:
        stripped = value.strip()
        if len(stripped) < 20:
            return False
        return stripped.startswith("#") or "\n#" in stripped or "$" in stripped or "|" in stripped

    def _compact_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        compact: Dict[str, Any] = {}
        for key in ("code", "msg", "message", "status", "state", "task_id", "taskId", "id"):
            value = self._first_value(payload, (key,))
            if value not in (None, ""):
                compact[key] = value
        return compact
