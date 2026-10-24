#!/usr/bin/env bash
# Install bootstrap review wrappers onto PATH for The-Big-1 doctor.
# Does NOT install speech or render — those must be real open tools.
set -euo pipefail

DEST="${1:-/machine/bin}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$DEST"
cp "$SCRIPT_DIR/video_review_wrapper.py" "$DEST/video-perception-review"
cp "$SCRIPT_DIR/audio_review_wrapper.py" "$DEST/audio-perception-review"
chmod +x "$DEST/video-perception-review" "$DEST/audio-perception-review"

echo "Installed:"
echo "  $DEST/video-perception-review"
echo "  $DEST/audio-perception-review"
echo
echo "Ensure $DEST is on PATH, then point local_tools.json at these names."
echo "Speech + render still require real open binaries (piper, comfyui-cli, ...)."
