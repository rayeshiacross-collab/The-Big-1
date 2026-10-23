"""Append-only run ledger. Source of truth for status and recovery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LEDGER_PATH, ensure_dirs


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ledger_file(run_id: str) -> Path:
    ensure_dirs()
    return LEDGER_PATH / f"{run_id}.jsonl"


def append_event(
    run_id: str,
    *,
    content_id: str,
    lane: str,
    status: str,
    files: list[str] | None = None,
    error: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    event = {
        "ts": _now_iso(),
        "run_id": run_id,
        "content_id": content_id,
        "lane": lane,
        "status": status,
        "files": files or [],
        "error": error,
        "extra": extra or {},
    }
    path = ledger_file(run_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events(run_id: str) -> list[dict[str, Any]]:
    path = ledger_file(run_id)
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def last_status(run_id: str, content_id: str) -> str | None:
    events = [e for e in read_events(run_id) if e.get("content_id") == content_id]
    if not events:
        return None
    return events[-1].get("status")
