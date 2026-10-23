"""Quality gates — fail closed. Partial work is not success."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


class QualityGateError(Exception):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__("Quality gate failed: " + "; ".join(missing))


def require_files(paths: Iterable[Path], labels: Iterable[str] | None = None) -> None:
    missing = []
    labels = list(labels) if labels else [str(p) for p in paths]
    for path, label in zip(paths, labels):
        if not Path(path).exists():
            missing.append(f"missing file: {label}")
    if missing:
        raise QualityGateError(missing)


def require_non_empty(path: Path, min_chars: int = 50, label: str | None = None) -> None:
    p = Path(path)
    if not p.exists():
        raise QualityGateError([f"missing file: {label or p}"])
    text = p.read_text(encoding="utf-8").strip()
    if len(text) < min_chars:
        raise QualityGateError([f"too short ({len(text)} chars): {label or p}"])


def psychology_gate(
    *,
    flagship: Path,
    short1: Path,
    short2: Path,
    short3: Path,
    companion: Path,
) -> None:
    require_files(
        [flagship, short1, short2, short3, companion],
        ["flagship_script", "short_1", "short_2", "short_3", "companion_article"],
    )
    require_non_empty(flagship, min_chars=2000, label="flagship_script")
    for s, name in ((short1, "short_1"), (short2, "short_2"), (short3, "short_3")):
        require_non_empty(s, min_chars=80, label=name)
    require_non_empty(companion, min_chars=800, label="companion_article")


def glitch_gate(*, script: Path, scene_plan: Path) -> None:
    require_files([script, scene_plan], ["glitch_script", "scene_plan"])
    require_non_empty(script, min_chars=100, label="glitch_script")
    require_non_empty(scene_plan, min_chars=100, label="scene_plan")
