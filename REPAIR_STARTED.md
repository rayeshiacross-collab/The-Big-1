# Repair process started — 2026-10-23

**Decision:** Keep The-Big-1 as the single control plane. Repair the existing production path. Do not build a competing engine.

## What was done in this session

1. Mapped the full production path and every fail-closed gate.
2. Confirmed Psychology runner already delegates to `src.autonomous_video`.
3. Confirmed Hypit is still a stub (next integration after first real video).
4. Cloned the hub and ran the full regression suite: **35 tests OK**.
5. Added a self-contained `repair/` overlay with:
   - `config/standing_policy.json`
   - `config/local_tools.json` (REPLACE placeholders)
   - `scripts/drive_verifier.py`
   - `scripts/dry_run.sh`
   - `docs/OPERATOR_CHECKLIST.md`

No overnight render was started. No lane repos were modified. No publishing path was enabled.

## Hub health (verified here)

```
python -m unittest discover -s tests -v
→ Ran 35 tests in ~8.5s — OK
```

The control plane itself is sound. Remaining work is runtime provisioning on a persistent machine.

## Next actions (on the production machine)

### A. One-time provisioning

```bash
# 1. Persistent checkout
git clone https://github.com/rayeshiacross-collab/The-Big-1.git /machine/The-Big-1
cd /machine/The-Big-1

# 2. Hermes at pinned commit
bash tools/install_hermes_local.sh /machine/runtime
# put the resulting hermes binary on PATH

# 3. Local model
ollama pull llama3.1:8b-instruct-q5_K_M
ollama serve   # must stay on 127.0.0.1

# 4. Open tools — install real binaries for:
#    speech  (piper / kokoro / supertonic3)
#    render  (ComfyUI open workflow wrapper)
#    video_review + audio_review (emit full-coverage receipts)

# 5. Place configs
cp repair/config/standing_policy.json /machine/standing_policy.json
cp repair/config/local_tools.json     /machine/local_tools.json
# edit local_tools.json — replace every REPLACE_* with absolute paths
```

### B. First production attempt

```bash
cd /machine/The-Big-1
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m src.runner doctor          # must be reachable + exact OK

export POLICY=/machine/standing_policy.json
export TOOLS=/machine/local_tools.json
export CONTENT_ID=psych-$(date +%Y%m%d)-first
export SCRIPT=/path/to/real-narration.txt

bash repair/scripts/dry_run.sh
# or via Psychology lane:
# python /path/to/rebootv2-psychology-runner/src/runner.py produce \
#   --hub-root /machine/The-Big-1 \
#   --content-id $CONTENT_ID --script $SCRIPT \
#   --policy $POLICY --tools $TOOLS
```

Success terminal state: **`READY_FOR_OWNER_INSPECTION`**  
Nothing publishes. You remain the only release gate.

### C. Optional Drive leave-draft

```bash
export GOOGLE_DRIVE_CREDENTIALS_PATH=/machine/drive-credentials.json
export GOOGLE_DRIVE_ROOT_FOLDER_ID=...
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
# then pass drive_verifier into mark_complete
```

## Hard rules still in force

- Open stack only
- content_id is forever
- No host / no cyborg
- Fail closed on missing tools, static video, incomplete perception
- Human only sets `RELEASE_APPROVED`

## Status

| Item | State |
|------|--------|
| Inspection | Complete |
| Hub regression | 35/35 pass |
| Repair overlay | Added under `repair/` |
| Overnight render | Not started |
| Repo push | Branch + PR (this commit) |
| Real end-to-end video | Outstanding — blocked only on machine tools |

When the four local tools are registered and doctor is green, the production path is ready for the first real short.
