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

Must report reachable before any real work.

## 4. Claim a handoff (after DC creates one)

```bash
python -m src.runner claim --lane psychology --content-id psych-20261022-autonomy-cost
```

## 5. What the skeleton already does

- Loads open-stack config
- Refuses paid APIs by default
- Append-only ledger
- Handoff load/claim
- Local model chat helper
- Quality-gate helpers
- Local file save (Drive upload stubbed)

Lane-specific writing logic still lives in the five private repos / Hermes skills. This skeleton is the shared backbone.
