"""Deterministic quality gates. Semantic review remains a human responsibility."""
import re
from pathlib import Path
from .config import CONFIG
class QualityGateError(Exception): pass

def require_files(paths, labels=None):
    paths = list(paths)
    labels = [str(p) for p in paths] if labels is None else list(labels)
    if not paths or len(paths) != len(labels): raise QualityGateError('Empty or mismatched required files')
    bad = [label for p, label in zip(paths, labels) if not Path(p).is_file() or Path(p).stat().st_size == 0]
    if bad: raise QualityGateError('Missing/empty files: ' + ', '.join(bad))

def require_non_empty(path, min_chars=50, label=None):
    require_files([path]); text = Path(path).read_text(encoding='utf-8').strip()
    if len(text) < min_chars: raise QualityGateError(f'Too short: {label or path}')
    if re.search(r'\[\s*VERIFY\b[^\]]*\]', text, re.I): raise QualityGateError('Unresolved VERIFY flag')
    for term in CONFIG['quality']['banned_terms']:
        if re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.I): raise QualityGateError('Banned term')
    return text

def words(path, minimum, maximum=None):
    text = require_non_empty(path)
    n = len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", text))
    if n < minimum or (maximum is not None and n > maximum): raise QualityGateError(f'Word count {n} out of bounds: {path}')

def psychology_gate(*, flagship, short1, short2, short3, companion):
    q = CONFIG['quality']
    words(flagship, q['flagship_min_words'], q['flagship_max_words'])
    for s in (short1, short2, short3): words(s, q['short_min_words'])
    words(companion, q['companion_min_words'])
    shorts = [Path(s).read_text().strip().casefold() for s in (short1, short2, short3)]
    if len(set(shorts)) != 3: raise QualityGateError('Shorts must be distinct')

def glitch_gate(*, script, scene_plan):
    words(script, 40)
    require_non_empty(scene_plan, 100)
