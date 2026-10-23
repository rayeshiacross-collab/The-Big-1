"""Machine-owned append-only usage history, including failed/interrupted attempts."""
import contextvars
import functools
import inspect
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from filelock import FileLock
from .config import ROOT, TZ
from zoneinfo import ZoneInfo

_current = contextvars.ContextVar('hub_execution', default=None)

def usage_path():
    return Path(os.environ.get('MACHINE_LEDGER_PATH', str(ROOT / 'ledgers' / 'machine_usage.jsonl')))

def _append(event):
    path = usage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + '.lock', timeout=10):
        with path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            f.flush(); os.fsync(f.fileno())

def tracked(operation):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            execution = _current.get()
            root = execution is None
            execution = execution or uuid.uuid4().hex
            operation_id = uuid.uuid4().hex
            # Explicit allowlist only: never serialize arguments, tokens or credentials.
            bound = inspect.signature(fn).bind(*args, **kwargs).arguments
            fields = {}
            from .safety import content_id, run_id, lane
            for key, validator in [('content_id', content_id), ('run_id', run_id), ('lane', lane)]:
                if key in bound:
                    try: fields[key] = validator(bound[key])
                    except (ValueError, TypeError): fields[key] = 'INVALID'
            token = _current.set(execution)
            started = datetime.now(timezone.utc)
            base = dict(execution_id=execution, operation_id=operation_id, operation=operation, root_operation=root, **fields)
            try:
                # No work starts if the machine cannot record the attempt.
                _append(dict(base, event='STARTED', timestamp=started.isoformat(), local_time=started.astimezone(ZoneInfo(TZ)).isoformat()))
                try:
                    result = fn(*args, **kwargs)
                except BaseException as exc:
                    _append(dict(base, event='FAILED', timestamp=datetime.now(timezone.utc).isoformat(), error_type=type(exc).__name__))
                    raise
                _append(dict(base, event='SUCCEEDED', timestamp=datetime.now(timezone.utc).isoformat()))
                return result
            finally:
                _current.reset(token)
        return wrapper
    return decorate

def recent_runs(limit=20):
    path = usage_path()
    if not path.exists(): return []
    rows = {}
    with FileLock(str(path) + '.lock', timeout=10):
        events = [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
    for e in events:
        if not e['root_operation']: continue
        row = rows.setdefault(e['operation_id'], {k:v for k,v in e.items() if k != 'event'})
        row['result'] = 'STARTED_NO_END_RECORDED' if e['event']=='STARTED' else e['event']
        if e['event'] != 'STARTED':
            row['ended_at']=e['timestamp']
            if 'error_type' in e: row['error_type']=e['error_type']
    return list(rows.values())[-limit:]
