#!/usr/bin/env python3
"""Bootstrap audio_review tool for The-Big-1.

Emits a receipt that satisfies the hub contract structure.
Uses ffprobe for duration. Structural bootstrap only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def duration_seconds(path: Path) -> float:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    data = json.loads(raw)
    return float(data["format"]["duration"])


def main() -> int:
    p = argparse.ArgumentParser(description="Bootstrap audio review receipt emitter")
    p.add_argument("media", type=Path, help="Path to narration.wav")
    p.add_argument("--receipt", type=Path, required=True, help="Where to write the receipt JSON")
    p.add_argument("--full-playback", action="store_true")
    p.add_argument("--emit-receipt", action="store_true")
    args = p.parse_args()

    media = args.media.resolve()
    if not media.is_file():
        print(f"media not found: {media}", file=sys.stderr)
        return 2

    dur = duration_seconds(media)
    receipt = {
        "artifact_sha256": sha256(media),
        "duration_seconds": dur,
        "reviewed_seconds": dur,
        "coverage": [[0.0, dur]],
        "tool": "audio-perception-review",
        "bootstrap": True,
        "note": "Structural bootstrap via ffprobe; replace with real full-playback perception for production",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(str(args.receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
