"""Load environment and basic paths. Open-stack only."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Local model (required) ---
LOCAL_MODEL_BASE_URL = os.getenv("LOCAL_MODEL_BASE_URL", "http://127.0.0.1:11434")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "llama3.1:8b-instruct-q5_K_M")
LOCAL_MODEL_LARGE = os.getenv("LOCAL_MODEL_LARGE", "")

# --- Paths ---
ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = Path(os.getenv("LEDGER_PATH", ROOT / "ledgers"))
HANDOFF_PATH = Path(os.getenv("HANDOFF_PATH", ROOT / "handoffs"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", ROOT / "output"))

# --- Drive (optional) ---
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "")
GOOGLE_DRIVE_ROOT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID", "")

# --- Safety ---
ALLOW_PAID_APIS = os.getenv("ALLOW_PAID_APIS", "0") == "1"
TZ = os.getenv("TZ", "America/Chicago")


def ensure_dirs() -> None:
    for p in (LEDGER_PATH, HANDOFF_PATH, OUTPUT_PATH):
        p.mkdir(parents=True, exist_ok=True)


def assert_open_stack() -> None:
    if ALLOW_PAID_APIS:
        raise RuntimeError(
            "ALLOW_PAID_APIS=1 is set. Open Stack Policy forbids paid APIs by default."
        )
