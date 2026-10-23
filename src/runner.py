"""Validated writing orchestration. No publisher or release-approval endpoint."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from .config import TZ, assert_open_stack, ensure_dirs, OUTPUT_PATH
from .handoff import Handoff, claim, claim_file, verify_claim, abandon_claim
from .ledger import _append, storage_lock
from .local_model import doctor_check
from . import validators, drive_storage
from .safety import confined

def central_now(): return datetime.now(ZoneInfo(TZ))
def make_run_id(): return central_now().strftime('%Y%m%d-%H%M-central')
def doctor():
    assert_open_stack(); ensure_dirs()
    result = doctor_check(); print('DOCTOR REPORT', result)
    if not result.get('reachable') or not result.get('ok'): raise SystemExit('Local doctor failed; fix before work')
def start_lane(lane, content_id):
    doctor()
    return claim(content_id, lane)

def mark_complete(run_id, content_id, lane, files, status='WRITING_COMPLETE', *, claim_token=None, drive_verifier=None):
    assert_open_stack()
    if status != 'WRITING_COMPLETE': raise PermissionError('Rendering/release gates require separate reviewed implementations')
    with storage_lock():
        h = Handoff.load(content_id)
        if h.run_id != run_id or h.target_lane != lane: raise PermissionError('Handoff identity mismatch')
        if not claim_token: raise PermissionError('Claim token required')
        verify_claim(h, claim_token)
        root = confined(OUTPUT_PATH, content_id)
        paths = [Path(p).resolve() for p in files]
        if any(not p.is_relative_to(root) for p in paths): raise ValueError('Output outside content folder')
        validators.require_files(paths)
        required = [confined(root, name) for name in h.required_assets]
        if not required or not set(required).issubset(paths): raise validators.QualityGateError('Required assets absent from completion')
        validators.require_files(required)
        by_name = {p.name: p for p in paths}
        if len(by_name) != len(paths): raise validators.QualityGateError('Duplicate asset names')
        if lane == 'psychology' and h.asset_profile == 'psychology_short':
            if not {'script.txt', 'scene_plan.json'}.issubset(by_name): raise validators.QualityGateError('Standalone Short package incomplete')
            validators.psychology_short_gate(script=by_name['script.txt'], scene_plan=by_name['scene_plan.json'])
        elif lane == 'psychology':
            names = ['flagship.txt', 'short1.txt', 'short2.txt', 'short3.txt', 'companion.txt']
            if not set(names).issubset(by_name): raise validators.QualityGateError('Psychology package missing required files')
            validators.psychology_gate(**dict(zip(['flagship', 'short1', 'short2', 'short3', 'companion'], [by_name[n] for n in names])))
        elif lane == 'system-glitch':
            if not {'script.txt', 'scene_plan.txt'}.issubset(by_name): raise validators.QualityGateError('Glitch package incomplete')
            validators.glitch_gate(script=by_name['script.txt'], scene_plan=by_name['scene_plan.txt'])
        else:
            raise NotImplementedError('No certified completion gate for this lane')
        for p in paths: validators.require_non_empty(p)
        available = set(drive_storage.list_outputs(content_id))
        if not set(paths).issubset({p.resolve() for p in available}): raise validators.QualityGateError('Storage inventory mismatch')
        # The bundled Drive helper is local-only. No receipt flag can masquerade as a provider readback.
        if drive_verifier is None: raise RuntimeError('Real Drive upload/readback adapter required; local-only completion remains draft')
        if drive_verifier(content_id, paths) is not True: raise RuntimeError('Drive verification failed')
        _append(run_id, content_id=content_id, lane=lane, status=status, files=[str(p) for p in paths])
        claim_file(content_id).unlink()
    print(f'{status}: {content_id}')

def main():
    p = argparse.ArgumentParser(description='Hub writing tools; no publication')
    p.add_argument('command', choices=['doctor', 'claim', 'abandon'])
    p.add_argument('--lane', default=''); p.add_argument('--content-id', default=''); p.add_argument('--claim-token', default='')
    args = p.parse_args()
    if args.command == 'doctor': doctor()
    elif args.command == 'claim':
        h = start_lane(args.lane, args.content_id)
        print(h.to_dict()); print('CLAIM_TOKEN=' + h.claim_token)
    else: abandon_claim(args.content_id, args.lane, args.claim_token)
if __name__ == '__main__': main()
