#!/usr/bin/env bash
# The-Big-1 end-to-end dry-run helper
# Run on a persistent machine that already has Hermes + local model + tools.
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
POLICY="${POLICY:-/machine/standing_policy.json}"
TOOLS="${TOOLS:-/machine/local_tools.json}"
OUTPUT="${OUTPUT:-$REPO_ROOT/output}"
CONTENT_ID="${CONTENT_ID:-psych-$(date +%Y%m%d)-dryrun}"
SCRIPT="${SCRIPT:-/tmp/test-narration.txt}"

echo "=== The-Big-1 dry-run ==="
echo "REPO_ROOT=$REPO_ROOT"
echo "CONTENT_ID=$CONTENT_ID"
echo "POLICY=$POLICY"
echo "TOOLS=$TOOLS"
echo "SCRIPT=$SCRIPT"
echo "OUTPUT=$OUTPUT"
echo

cd "$REPO_ROOT"

if [[ ! -f "$SCRIPT" ]]; then
  cat > "$SCRIPT" <<'EOF'
A promotion can feel like a loss when it costs autonomy, evenings, and the capacity to care for the people who need you. The title looks better on paper. The calendar tells a different story.
EOF
  echo "Created sample narration at $SCRIPT"
fi

echo "1. Doctor check"
python -m src.runner doctor

echo
echo "2. Autonomous video (script-only)"
python -m src.autonomous_video \
  --content-id "$CONTENT_ID" \
  --script "$SCRIPT" \
  --policy "$POLICY" \
  --tools "$TOOLS" \
  --output "$OUTPUT"

echo
echo "3. Inspect latest attempt"
LATEST=$(find "$OUTPUT/$CONTENT_ID" -maxdepth 1 -type d -name '20*' | sort | tail -1 || true)
if [[ -n "$LATEST" ]]; then
  echo "Attempt dir: $LATEST"
  ls -la "$LATEST"/attempt_* 2>/dev/null || true
  if [[ -f "$LATEST"/run_status.json ]]; then
    echo "--- run_status.json ---"
    cat "$LATEST"/run_status.json
  fi
  for f in blocked.json validation_failure.json verified_delivery.json; do
    found=$(find "$LATEST" -name "$f" | head -1 || true)
    if [[ -n "$found" ]]; then
      echo "--- $found ---"
      cat "$found"
    fi
  done
else
  echo "No attempt directory found under $OUTPUT/$CONTENT_ID"
fi

echo
echo "4. Machine usage (recent)"
python -m src.runner runs || true

echo
echo "Done. Status READY_FOR_OWNER_INSPECTION means the package is ready for your review."
echo "Nothing was published."
