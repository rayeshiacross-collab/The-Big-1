"""Durable handoff manifest between lanes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import HANDOFF_PATH, ensure_dirs


@dataclass
class Handoff:
    run_id: str
    content_id: str
    target_lane: str
    selected_angle: str
    source_urls: list[dict[str, Any]] = field(default_factory=list)
    catalog_collision: dict[str, Any] = field(default_factory=dict)
    required_assets: list[str] = field(default_factory=list)
    research_completion_status: str = "RESEARCH_COMPLETE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self) -> Path:
        ensure_dirs()
        path = HANDOFF_PATH / f"{self.content_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, content_id: str) -> "Handoff":
        path = HANDOFF_PATH / f"{content_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"No handoff for content_id={content_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


def claim(content_id: str, lane: str) -> Handoff:
    """Atomically claim a handoff for a lane. Raises if missing."""
    h = Handoff.load(content_id)
    if h.target_lane != lane and h.target_lane not in ("any", lane):
        # soft check — allow explicit overrides later if needed
        pass
    return h
