# Machine provisioning — continue the repair

This is the active repair step. The hub is healthy. Everything below runs on a **persistent** host (not ephemeral CI).

## Order of operations

### Step 1 — Checkout the repair branch

```bash
git clone -b repair/production-path \
  https://github.com/rayeshiacross-collab/The-Big-1.git /machine/The-Big-1
cd /machine/The-Big-1
```

### Step 2 — Hermes (pinned)

```bash
bash tools/install_hermes_local.sh /machine/runtime
export PATH="/machine/runtime/hermes-agent/.venv/bin:$PATH"
hermes chat --help | head   # must show --safe-mode --oneshot --query-file --base-url
```

### Step 3 — Local model (loopback only)

```bash
ollama pull llama3.1:8b-instruct-q5_K_M
ollama serve   # binds 127.0.0.1:11434
curl -s http://127.0.0.1:11434/v1/models | head
```

### Step 4 — Four local tools

| Capability | What to install | Notes |
|------------|-----------------|-------|
| `speech` | Piper / Kokoro / Supertonic3 | Must be on PATH; note absolute model path |
| `render` | ComfyUI + open workflow wrapper | Loopback endpoint only |
| `video_review` | Wrapper that emits full-coverage receipt | See PERCEPTION_RECEIPT_CONTRACT.md |
| `audio_review` | Wrapper that emits full-coverage receipt | Same contract |

Also required on PATH: `ffmpeg`, `ffprobe`.

### Step 5 — Fill configs

```bash
cp repair/config/standing_policy.json /machine/standing_policy.json
cp repair/config/local_tools.json     /machine/local_tools.json
```

Edit `/machine/local_tools.json`:
- Set `"model"` to the exact id returned by `/v1/models`
- Replace every `REPLACE_*` with real absolute paths / binary names
- Ensure all four capabilities are present

### Step 6 — Doctor

```bash
cd /machine/The-Big-1
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.runner doctor
# MUST print reachable + exact OK before any claim or produce
```

### Step 7 — First production attempt

```bash
export POLICY=/machine/standing_policy.json
export TOOLS=/machine/local_tools.json
export CONTENT_ID=psych-$(date +%Y%m%d)-first
export SCRIPT=/path/to/real-narration.txt   # plain TXT only

bash repair/scripts/dry_run.sh
```

Or via Psychology lane (already wired):

```bash
python /path/to/rebootv2-psychology-runner/src/runner.py produce \
  --hub-root /machine/The-Big-1 \
  --content-id "$CONTENT_ID" \
  --script "$SCRIPT" \
  --policy "$POLICY" \
  --tools "$TOOLS"
```

### Step 8 — Inspect

Look under `output/<content_id>/<timestamp>/`:
- `attempt_NN/verified_delivery.json` → status `READY_FOR_OWNER_INSPECTION`
- or `blocked.json` / `validation_failure.json` → fix and re-run same content_id

## If doctor fails

| Error | Fix |
|-------|-----|
| Hermes is not installed | Step 2 |
| FFmpeg / ffprobe required | `apt install ffmpeg` (or equivalent) |
| Missing configured local capabilities | Step 4–5 — all four must be registered |
| Local model inventory unreachable | Step 3 — loopback only, no proxy |
| Configured local model is not available | Model name in tools.json must match `/v1/models` |

## If produce fails after doctor is green

1. Open the attempt directory
2. Read `blocked.json` or `validation_failure.json`
3. Common causes: static video, incomplete scene coverage, missing perception receipts, narration altered
4. Fix the tool / re-run the **same** content_id (idempotent)

## What this repair does NOT do

- Register a self-hosted GitHub runner
- Start a background / overnight render
- Publish or set RELEASE_APPROVED
- Modify the five lane repos (Psychology is already wired; Hypit is next after first video)
