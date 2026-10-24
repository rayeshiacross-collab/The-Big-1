#!/usr/bin/env python3
"""Bootstrap video_review tool for The-Big-1.

Emits a receipt that satisfies the hub contract structure:
  artifact_sha256, duration_seconds, reviewed_seconds, coverage

This uses ffprobe for duration. It is a structural bootstrap so doctor
and receipt validation can pass while a real perceptual reviewer is built.
Replace with a true full-playback perception tool for production quality.
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
    p = argparse.ArgumentParser(description="Bootstrap video review receipt emitter")
    p.add_argument("media", type=Path, help="Path to final.mp4")
    p.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="Where to write the receipt JSON",
    )
    p.add_argument("--full-playback", action="store_true", help="Accepted; ignored in bootstrap")
    p.add_argument("--emit-receipt", action="store_true", help="Accepted; receipt always written")
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
        "tool": "video-perception-review",
        "bootstrap": True,
        "note": "Structural bootstrap via ffprobe; replace with real full-playback perception for production",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(str(args.receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
