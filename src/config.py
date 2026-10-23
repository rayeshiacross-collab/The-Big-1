"""Load the shared YAML contract, with explicit environment overrides."""
import os
from pathlib import Path
from urllib.parse import urlsplit
import ipaddress
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv()
CONFIG = yaml.safe_load((ROOT / 'config/runner.yaml').read_text())
def configured_path(key, env):
    p = Path(os.getenv(env, CONFIG['paths'][key]))
    return p if p.is_absolute() else ROOT / p
LEDGER_PATH = configured_path('ledger', 'LEDGER_PATH')
HANDOFF_PATH = configured_path('handoff', 'HANDOFF_PATH')
OUTPUT_PATH = configured_path('output', 'OUTPUT_PATH')
LOCAL_MODEL_BASE_URL = os.getenv('LOCAL_MODEL_BASE_URL', CONFIG['model']['base_url'])
LOCAL_MODEL_NAME = os.getenv('LOCAL_MODEL_NAME', CONFIG['model']['name'])
LOCAL_MODEL_LARGE = os.getenv('LOCAL_MODEL_LARGE', CONFIG['model'].get('large', ''))
LOCAL_MODEL_PROTOCOL = os.getenv('LOCAL_MODEL_PROTOCOL', CONFIG['model'].get('protocol', 'ollama'))
ALLOW_PAID_APIS = os.getenv('ALLOW_PAID_APIS', '0')
TZ = os.getenv('TZ', CONFIG['timezone'])
STATUS_VOCABULARY = frozenset(CONFIG['status_vocabulary'])
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', '')
GOOGLE_DRIVE_ROOT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID', '')

def ensure_dirs():
    for p in (LEDGER_PATH, HANDOFF_PATH, OUTPUT_PATH):
        p.mkdir(parents=True, exist_ok=True)

def assert_open_stack():
    if ALLOW_PAID_APIS not in ('0', 'false', 'False') or CONFIG['safety']['allow_paid_apis'] is not False:
        raise RuntimeError('Paid APIs are forbidden; no override is supported')
    u = urlsplit(LOCAL_MODEL_BASE_URL)
    try:
        host = ipaddress.ip_address(u.hostname or '')
    except ValueError:
        raise RuntimeError('Model endpoint must use a loopback IP literal') from None
    if not host.is_loopback or u.scheme != 'http' or u.username or u.password or u.query or u.fragment or u.path not in ('', '/', '/v1', '/v1/'):
        raise RuntimeError('Only local loopback HTTP model endpoints are allowed')
    if LOCAL_MODEL_PROTOCOL not in ('ollama', 'openai'):
        raise RuntimeError('LOCAL_MODEL_PROTOCOL must be ollama or openai')
