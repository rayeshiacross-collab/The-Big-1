"""Validated identities and confined paths; never derive paths from unchecked input."""
import re
from datetime import datetime
from pathlib import Path

LANES = {'psychology', 'system-glitch', 'hypit', 'omni', 'master-research'}

def content_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'(psych|glitch|hypit|omni)-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 160:
        raise ValueError('Invalid content_id')
    datetime.strptime(value.split('-')[1], '%Y%m%d')
    return value

def run_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{8}-\d{4}-central', value):
        raise ValueError('Invalid run_id')
    datetime.strptime(value, '%Y%m%d-%H%M-central')
    return value

def lane(value):
    if value not in LANES:
        raise ValueError('Unknown lane')
    return value

def confined(root, *parts):
    root = Path(root).resolve()
    for part in parts:
        p = Path(part)
        if not part or p.is_absolute() or '..' in p.parts or '\\' in str(part):
            raise ValueError('Unsafe relative path')
    dest = root.joinpath(*parts).resolve()
    if not dest.is_relative_to(root) or dest == root:
        raise ValueError('Path escapes storage root')
    return dest
