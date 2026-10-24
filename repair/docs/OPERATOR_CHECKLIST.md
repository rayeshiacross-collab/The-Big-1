# The-Big-1 Repair Package — Operator Checklist

Keep The-Big-1 as the single control plane. Repair the existing production path.

## 0. Machine prerequisites (one-time)

- [ ] Persistent disk (not an ephemeral Actions workspace)
- [ ] Python 3.11+ (3.12/3.14 fine)
- [ ] FFmpeg + ffprobe on PATH
- [ ] Local model server on loopback (Ollama recommended)
  ```bash
  ollama pull llama3.1:8b-instruct-q5_K_M
  ollama serve
  ```
- [ ] Hermes installed at a fixed commit
  ```bash
  bash tools/install_hermes_local.sh /machine/runtime
  # ensure the resulting hermes binary is on PATH
  ```
- [ ] Open speech engine (Piper / Kokoro / Supertonic3 / …)
- [ ] Open render path (ComfyUI + open workflow, or equivalent)
- [ ] Local perception wrappers that emit full-coverage receipts for video **and** audio
- [ ] (Optional) Google Drive OAuth credentials for the verifier

## 1. Place configs on the machine

```bash
cp repair/config/standing_policy.json /machine/standing_policy.json
cp repair/config/local_tools.json     /machine/local_tools.json
# edit local_tools.json — replace every REPLACE_* with real absolute paths / binaries
```

## 2. Doctor must pass

```bash
cd /path/to/The-Big-1
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.runner doctor
# must report reachable AND exact OK
```

## 3. First real production attempt

```bash
export POLICY=/machine/standing_policy.json
export TOOLS=/machine/local_tools.json
export CONTENT_ID=psych-$(date +%Y%m%d)-first
export SCRIPT=/path/to/real-narration.txt   # plain TXT only

bash repair/scripts/dry_run.sh
# or the expanded commands inside that script
```

Expected success terminal state: `READY_FOR_OWNER_INSPECTION`  
Expected artifacts under `output/<content_id>/<timestamp>/attempt_NN/`:

- final.mp4, narration.wav, narration.txt, captions.srt
- thumbnail.jpg, youtube.json, hermes_plan.json
- self_qa.json + perception receipts
- verified_delivery.json

## 4. Drive verifier (optional, required for leaving draft)

```bash
export GOOGLE_DRIVE_CREDENTIALS_PATH=/machine/drive-credentials.json
export GOOGLE_DRIVE_ROOT_FOLDER_ID=your-root-folder-id
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

# smoke test
python repair/scripts/drive_verifier.py some-content-id /path/to/file1 /path/to/file2
```

Wire into `mark_complete(..., drive_verifier=drive_verifier)`.

## 5. Hard rules (do not break)

- Open stack only — no paid APIs
- content_id is forever
- No host / no cyborg
- Human is the only RELEASE_APPROVED gate
- Fail closed on missing tools, static video, incomplete perception, or Drive mismatch

## 6. If anything fails

1. Read `blocked.json` or `validation_failure.json` in the attempt directory
2. Re-run `python -m src.runner doctor`
3. Fix the missing executable / model / receipt
4. Re-run the same content_id (idempotent — does not invent a second episode)

Nothing in this package starts an overnight render, registers a runner, or publishes.
