"""Durable manifests and exclusive, persistent claims."""
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import HANDOFF_PATH, ensure_dirs
from .safety import content_id as valid_content, run_id as valid_run, lane as valid_lane, confined
from .ledger import storage_lock, last_status, _append, PROTECTED

@dataclass
class Handoff:
    run_id: str
    content_id: str
    target_lane: str
    selected_angle: str
    source_urls: list[dict[str, Any]] = field(default_factory=list)
    catalog_collision: dict[str, Any] = field(default_factory=dict)
    required_assets: list[str] = field(default_factory=list)
    research_completion_status: str = 'RESEARCH_COMPLETE'
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def validate(self):
        valid_run(self.run_id); valid_content(self.content_id); valid_lane(self.target_lane)
        if self.research_completion_status != 'RESEARCH_COMPLETE' or not self.selected_angle.strip():
            raise ValueError('Incomplete research handoff')
        for name in self.required_assets: confined(Path('/assets'), name)
    def to_dict(self): return asdict(self)
    def save(self):
        self.validate(); ensure_dirs()
        path = confined(HANDOFF_PATH, self.content_id + '.json')
        with storage_lock():
            if path.exists():
                if json.loads(path.read_text()) != self.to_dict(): raise FileExistsError('Existing handoff is immutable')
                return path
            with path.open('x', encoding='utf-8') as f: json.dump(self.to_dict(), f, indent=2)
        return path
    @classmethod
    def load(cls, content_id):
        path = confined(HANDOFF_PATH, valid_content(content_id) + '.json')
        h = cls(**json.loads(path.read_text())); h.validate()
        if h.content_id != content_id: raise ValueError('Handoff identity mismatch')
        return h

def claim_file(content_id): return confined(HANDOFF_PATH, valid_content(content_id) + '.claim.json')
def claim(content_id, lane):
    valid_lane(lane)
    with storage_lock():
        h = Handoff.load(content_id)
        if h.target_lane != lane: raise PermissionError('Handoff assigned to a different lane')
        prev = last_status(h.run_id, content_id)
        if prev in PROTECTED: raise RuntimeError(f'Already beyond writing: {prev}; no mutation applied')
        token = uuid.uuid4().hex
        p = claim_file(content_id)
        # Persistent claim survives process termination; recovery requires explicit abandon.
        with p.open('x', encoding='utf-8') as f:
            json.dump(dict(token=token, lane=lane, run_id=h.run_id), f)
        try:
            if prev != 'WRITING_IN_PROGRESS':
                _append(h.run_id, content_id=content_id, lane=lane, status='WRITING_IN_PROGRESS')
        except Exception:
            p.unlink(); raise
        h.claim_token = token
        return h

def verify_claim(h, token):
    c = json.loads(claim_file(h.content_id).read_text())
    if c != dict(token=token, lane=h.target_lane, run_id=h.run_id):
        raise PermissionError('Claim token/owner mismatch')

def abandon_claim(content_id, lane, token):
    with storage_lock():
        h = Handoff.load(content_id)
        if lane != h.target_lane: raise PermissionError('Wrong lane')
        verify_claim(h, token); claim_file(content_id).unlink()
