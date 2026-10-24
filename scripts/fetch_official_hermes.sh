#!/usr/bin/env bash
set -euo pipefail
# Source of truth: https://github.com/NousResearch/hermes-agent
# Keeps upstream separate from The-Big-1 production code.
UPSTREAM_URL="https://github.com/NousResearch/hermes-agent.git"
DEST="${1:-vendor/hermes-agent}"
REF="${HERMES_REF:-main}"
if [[ -e "$DEST" ]]; then
  echo "Refusing to overwrite existing $DEST" >&2
  exit 2
fi
mkdir -p "$(dirname "$DEST")"
git clone --filter=blob:none "$UPSTREAM_URL" "$DEST"
git -C "$DEST" checkout "$REF"
git -C "$DEST" rev-parse HEAD | tee "$DEST.UPSTREAM_COMMIT"
printf 'Official Hermes source fetched into %s; not installed or executed.\n' "$DEST"
