"""Append-only JSONL ledger, serialized across processes on one local filesystem."""
import json
from datetime import datetime, timezone
from filelock import FileLock
from .config import LEDGER_PATH, STATUS_VOCABULARY, ensure_dirs
from .safety import content_id as valid_content, run_id as valid_run, lane as valid_lane, confined

PROTECTED = {'WRITING_COMPLETE', 'RENDER_PENDING', 'VIDEO_QA_PASSED', 'RELEASE_APPROVED'}
def ledger_file(run_id):
    return confined(LEDGER_PATH, valid_run(run_id) + '.jsonl')
def storage_lock():
    ensure_dirs()
    return FileLock(str(LEDGER_PATH / '.hub.lock'), timeout=10)
def read_events(run_id):
    p = ledger_file(run_id)
    if not p.exists(): return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
def last_status(run_id, content_id):
    valid_content(content_id)
    events = [e for e in read_events(run_id) if e['content_id'] == content_id]
    return events[-1]['status'] if events else None

def _append(run_id, *, content_id, lane, status, files=None, error=None, extra=None):
    valid_content(content_id); valid_lane(lane); valid_run(run_id)
    if status not in STATUS_VOCABULARY: raise ValueError('Unknown status')
    if status == 'RELEASE_APPROVED':
        raise PermissionError('Automated release approval is forbidden; this hub cannot approve or publish')
    prev = last_status(run_id, content_id)
    allowed = {None: {'RESEARCH_COMPLETE', 'WRITING_IN_PROGRESS'}, 'RESEARCH_COMPLETE': {'WRITING_IN_PROGRESS'}, 'WRITING_IN_PROGRESS': {'WRITING_COMPLETE'}, 'WRITING_COMPLETE': {'RENDER_PENDING'}, 'RENDER_PENDING': {'VIDEO_QA_PASSED'}}
    if status not in allowed.get(prev, set()):
        raise ValueError(f'Illegal status transition: {prev} -> {status}')
    event = dict(ts=datetime.now(timezone.utc).isoformat(), run_id=run_id, content_id=content_id, lane=lane, status=status, files=files or [], error=error, extra=extra or {})
    with ledger_file(run_id).open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n'); f.flush()
        import os
        os.fsync(f.fileno())

def append_event(run_id, **kwargs):
    # Only runner's validated completion path may advance production gates.
    if kwargs.get('status') in {'WRITING_COMPLETE', 'RENDER_PENDING', 'VIDEO_QA_PASSED'}:
        raise PermissionError('Use validated runner completion, not raw status writes')
    with storage_lock(): _append(run_id, **kwargs)
