"""Fail-closed Hermes review receipts. Evidence is supplied by an actual reviewer.

This validates a review record, not whether a model honestly watched/listened.
No receipt is generated automatically and no publication approval is granted.
"""
import hashlib
from datetime import datetime
from pathlib import Path
from .validators import QualityGateError

WRITING_CHECKS = {'accuracy', 'completeness', 'scene_alignment'}
VIDEO_CHECKS = {'narration', 'visible_action', 'captions', 'timing', 'sound', 'continuity', 'technical_export', 'thumbnail', 'youtube_metadata'}

def require_self_qa(report, *, content_id, files, stage='writing'):
    if stage not in ('writing', 'video'):
        raise QualityGateError('Unknown self-QA stage')
    if not isinstance(report, dict) or report.get('reviewer') != 'Hermes' or report.get('content_id') != content_id or report.get('stage') != stage or report.get('verdict') != 'PASS':
        raise QualityGateError('Hermes self-QA PASS report required for this content and stage')
    try:
        reviewed = datetime.fromisoformat(report['reviewed_at'])
        if reviewed.tzinfo is None: raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise QualityGateError('Self-QA needs a dated review with timezone') from None
    if report.get('unresolved_issues') != []:
        raise QualityGateError('Unresolved self-QA issues block completion')
    paths = list(map(Path, files))
    expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if not expected or len(expected) != len(paths) or report.get('artifact_sha256') != expected:
        raise QualityGateError('Self-QA is missing, stale or references different artifacts')
    checks = report.get('checks')
    required = WRITING_CHECKS if stage == 'writing' else VIDEO_CHECKS
    if not isinstance(checks, dict): raise QualityGateError('Missing self-QA checks')
    for key in required:
        check = checks.get(key)
        if not isinstance(check, dict) or check.get('status') != 'PASS' or not isinstance(check.get('evidence'), str) or not check['evidence'].strip():
            raise QualityGateError('Self-QA missing passing evidence: ' + key)
    if stage == 'video' and (report.get('watched_full_video') is not True or report.get('listened_full_audio') is not True):
        raise QualityGateError('Full video and audio review required; sample frames are insufficient')
    return {'reviewer': 'Hermes', 'stage': stage, 'reviewed_at': report['reviewed_at'], 'artifact_sha256': expected}
