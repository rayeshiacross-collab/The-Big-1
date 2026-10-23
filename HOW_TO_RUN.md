# How to Run the Skeleton (Local First)

## 1. Prerequisites

- Python 3.11+
- A local model server (Ollama recommended)
- This repo cloned

```bash
# Example with Ollama
ollama pull llama3.1:8b-instruct-q5_K_M
ollama serve
```

## 2. Setup

```bash
cd The-Big-1
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env if needed
```

## 3. Doctor check

```bash
python -m src.runner doctor
```

Must report reachable **and** an exact `OK` reply before any claim. Use a loopback IP, with explicit `LOCAL_MODEL_PROTOCOL=ollama` or `openai`. Config is loaded from `config/runner.yaml`; environment variables override model/path settings.

## 4. Claim a handoff (after DC creates one)

```bash
python -m src.runner claim --lane psychology --content-id psych-20261022-autonomy-cost
```

## 5. What the skeleton already does

- Loads open-stack config
- Refuses paid APIs and non-loopback model endpoints
- Append-only ledger
- Validated immutable handoffs and persistent exclusive claims
- Local model chat helper
- Wired completion gates; missing real Drive verifier fails closed
- Local file save (Drive upload stubbed)

Lane-specific writing logic still lives in the five private repos / Hermes skills. This skeleton is the shared backbone.

## Tests and operational limits

Run `python -m unittest discover -s tests -v`. See HARDENING.md before integrating a lane. The manual Action only runs a doctor on an explicitly labeled self-hosted `hub-local` runner; without one it queues and cannot test a model. No hosted runner can access your laptop loopback. No workflow was dispatched as part of the patch. Claims must use persistent local storage, not ephemeral Actions workspaces.

Do not register a new runner or expose a model publicly just to satisfy the workflow. Local CLI operation is supported without a runner. Windows timezone data is included; Windows runtime behavior still needs testing on Windows.

## The ledger stays with the machine

The hub automatically appends STARTED and SUCCEEDED/FAILED events to `ledgers/machine_usage.jsonl` for doctor, claim, writing-completion and abandon operations. Direct runner API calls are tracked too. Nested doctor calls share the root execution ID so they are not counted as separate runs. View recent root uses with `python -m src.runner runs`.

Each record includes timestamps (UTC and Chicago at start), operation/execution IDs, content/run/lane IDs when supplied and outcome. No claim tokens, raw arguments, credentials or prompt text are logged. An unmatched STARTED event means no ending was recorded (still running or interrupted), not success. If the ledger cannot be written before work, work does not start.

Runtime history stays on the machine's persistent disk, ignored by Git. If the checkout is ephemeral, set MACHINE_LEDGER_PATH to a persistent mounted path; the repository does not provision a server or persistent disk. Keep this machine ledger separate from content-specific ledger paths so per-batch path overrides do not scatter the machine's usage history. Drive copies are optional backups, not the primary usage ledger. No pre-existing history is invented or backfilled as new runs.

Hub timezone uses `HUB_TIMEZONE` or YAML (America/Chicago), not the host system TZ variable. UTC timestamps remain authoritative.

## Autonomous video production

Use `python -m src.autonomous_video --help` and [docs/AUTONOMOUS_VIDEO.md](docs/AUTONOMOUS_VIDEO.md). This is the production entrypoint for script-only input and Hermes-authored scenes, assets, inspection and bounded repairs. It never consumes legacy scene jobs and never publishes automatically. No missing runtime is simulated.
