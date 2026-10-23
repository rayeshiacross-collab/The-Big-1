"""Drive storage stub.

Real Google Drive integration is optional.
For now this writes to local OUTPUT_PATH and records the intended Drive location.
Swap in the official google-api client later if desired — still free tier.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import OUTPUT_PATH, ensure_dirs


def save_text(
    content_id: str,
    filename: str,
    text: str,
    *,
    subfolder: str = "",
) -> Path:
    ensure_dirs()
    folder = OUTPUT_PATH / content_id
    if subfolder:
        folder = folder / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_text(text, encoding="utf-8")
    return path


def list_outputs(content_id: str) -> list[Path]:
    folder = OUTPUT_PATH / content_id
    if not folder.exists():
        return []
    return sorted(p for p in folder.rglob("*") if p.is_file())


def drive_placeholder_meta(local_path: Path, intended_drive_folder: str) -> dict[str, Any]:
    """Record where this should live in Drive once credentials are wired."""
    return {
        "local_path": str(local_path),
        "intended_drive_folder": intended_drive_folder,
        "uploaded": False,
        "note": "Wire google-api-python-client when ready; keep open-stack rules.",
    }
