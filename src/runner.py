"""Base runner — claim → work → validate → ledger → save.

Each lane subclasses or calls these helpers.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import TZ, assert_open_stack, ensure_dirs
from .handoff import Handoff, claim
from .ledger import append_event, last_status
from .local_model import doctor_check


def central_now() -> datetime:
    return datetime.now(ZoneInfo(TZ))


def make_run_id() -> str:
    return central_now().strftime("%Y%m%d-%H%M-central")


def doctor() -> None:
    assert_open_stack()
    ensure_dirs()
    result = doctor_check()
    print("DOCTOR REPORT")
    print(result)
    if not result.get("reachable"):
        raise SystemExit("Local model not reachable. Fix before running.")


def start_lane(lane: str, content_id: str) -> Handoff:
    """Claim handoff and mark WRITING_IN_PROGRESS."""
    assert_open_stack()
    ensure_dirs()
    h = claim(content_id, lane)
    run_id = h.run_id
    prev = last_status(run_id, content_id)
    if prev in ("WRITING_COMPLETE", "RENDER_PENDING", "VIDEO_QA_PASSED", "RELEASE_APPROVED"):
        print(f"Already past writing for {content_id} (status={prev}). Resuming carefully.")
    append_event(
        run_id,
        content_id=content_id,
        lane=lane,
        status="WRITING_IN_PROGRESS",
    )
    return h


def mark_complete(
    run_id: str,
    content_id: str,
    lane: str,
    files: list[str],
    status: str = "WRITING_COMPLETE",
) -> None:
    append_event(
        run_id,
        content_id=content_id,
        lane=lane,
        status=status,
        files=files,
    )
    print(f"{status}: {content_id} ({len(files)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description="REBOOTv2 base runner")
    parser.add_argument("command", choices=["doctor", "claim"])
    parser.add_argument("--lane", default="")
    parser.add_argument("--content-id", default="")
    args = parser.parse_args()

    if args.command == "doctor":
        doctor()
    elif args.command == "claim":
        if not args.lane or not args.content_id:
            raise SystemExit("--lane and --content-id required")
        h = start_lane(args.lane, args.content_id)
        print(h.to_dict())


if __name__ == "__main__":
    main()
