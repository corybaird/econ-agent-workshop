"""Zero-dependency Langfuse ingestion client for benchmark traces and rubric scores."""

import base64
import json
import logging
import os
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class LangfuseClient:
    """Post benchmark traces, per-turn generations, and scores to Langfuse."""

    def __init__(self, enabled=True):
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        base = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST") or ""
        self.base_url = base.rstrip("/")
        self.enabled = bool(enabled and self.public_key and self.secret_key and self.base_url)
        if enabled and not self.enabled:
            logger.warning("Langfuse env vars incomplete; skipping remote telemetry")

    def log_benchmark_run(self, record, tags=None):
        """Send one trace + per-turn generations + automated scores; return trace_id or None."""
        if not self.enabled:
            return None

        trace_id = str(uuid.uuid4())
        now_iso = datetime.now(UTC).isoformat()
        tag_list = list(tags) if tags is not None else []
        tag_list.extend([record["model_label"], record["arm_id"], record["task_id"]])

        batch = [
            {
                "id": str(uuid.uuid4()),
                "type": "trace-create",
                "timestamp": now_iso,
                "body": {
                    "id": trace_id,
                    "timestamp": record["started_at"],
                    "name": f"{record['model_label']} | {record['arm_id']} | {record['task_id']}",
                    "tags": tag_list,
                    "input": record["task_prompt"],
                    "output": record["final_reply"][:4000],
                    "metadata": {
                        "model_label": record["model_label"],
                        "provider": record["provider"],
                        "model": record["model"],
                        "arm_id": record["arm_id"],
                        "arm_label": record["arm_label"],
                        "task_id": record["task_id"],
                        "exit_code": record["exit_code"],
                        "wall_time_sec": record["wall_time_sec"],
                        "totals": record["usage"],
                        "rubric": record["rubric"],
                        "created_files": record["rubric"]["created_files"],
                    },
                },
            }
        ]

        for idx, turn in enumerate(record["turn_details"], start=1):
            batch.append({
                "id": str(uuid.uuid4()),
                "type": "generation-create",
                "timestamp": now_iso,
                "body": {
                    "id": str(uuid.uuid4()),
                    "traceId": trace_id,
                    "name": f"turn-{idx}",
                    "model": record["model"],
                    "startTime": turn["timestamp"],
                    "endTime": turn["timestamp"],
                    "output": turn["text"][:2000],
                    "usage": {
                        "input": turn["input"],
                        "output": turn["output"],
                        "total": turn["total"],
                        "unit": "TOKENS",
                    },
                    "metadata": {
                        "cache_read": turn["cache_read"],
                        "cache_write": turn["cache_write"],
                        "duration_ms": turn["duration_ms"],
                        "tool_calls": turn["tool_calls"],
                    },
                },
            })

        score_pairs = [
            ("total_tokens", record["usage"]["total_tokens"]),
            ("input_tokens", record["usage"]["input_tokens"]),
            ("output_tokens", record["usage"]["output_tokens"]),
            ("cache_read_tokens", record["usage"]["cache_read_tokens"]),
            ("turns", record["usage"]["turns"]),
            ("tool_calls", record["usage"]["tool_calls"]),
            ("skill_reads", record["usage"]["skill_reads"]),
            ("wall_time_sec", record["wall_time_sec"]),
            ("custom_python_loc", record["rubric"]["custom_python_loc"]),
            ("raw_data_untouched", int(record["rubric"]["raw_data_untouched"])),
            ("clean_root", int(record["rubric"]["clean_root"])),
            ("yaml_config_used", int(record["rubric"]["yaml_config_used"])),
            ("target_lib_ratio", record["rubric"]["target_lib_ratio"]),
            ("artifacts_ok", int(record["rubric"]["artifacts_ok"])),
            ("provenance_ok", int(record["rubric"]["provenance_ok"])),
            ("numerical_ok", int(record["rubric"].get("numerical_ok", True))),
            ("rubric_score", record["rubric"]["rubric_score"]),
        ]
        for name, value in score_pairs:
            batch.append({
                "id": str(uuid.uuid4()),
                "type": "score-create",
                "timestamp": now_iso,
                "body": {
                    "id": str(uuid.uuid4()),
                    "traceId": trace_id,
                    "name": name,
                    "value": float(value),
                },
            })

        self._post_batch(batch)
        return trace_id

    def _post_batch(self, batch):
        token = base64.b64encode(f"{self.public_key}:{self.secret_key}".encode()).decode()
        payload = json.dumps({"batch": batch}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/public/ingestion",
            data=payload,
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info("Langfuse ingestion status=%d events=%d", resp.status, len(batch))
        except urllib.error.URLError as exc:
            logger.warning("Langfuse ingestion failed: %s", exc)
