#!/usr/bin/env python3
"""Minimal Drive verifier that satisfies The-Big-1 mark_complete contract.

Returns exactly True only after upload + SHA-256 read-back of every path.
Never publishes. Never sets RELEASE_APPROVED.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
from typing import Sequence

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


def _service():
    creds = Credentials.from_authorized_user_file(
        _env("GOOGLE_DRIVE_CREDENTIALS_PATH"), SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def drive_verifier(content_id: str, paths: Sequence[Path]) -> bool:
    """
    Upload every path under a content_id folder, then download and
    compare SHA-256. Returns exactly the Python boolean True on full
    success. Any other return value or exception keeps the item in draft.
    """
    if not paths:
        return False

    root_folder_id = _env("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    svc = _service()

    # Locate or create the content_id folder under the configured root
    q = (
        f"name = '{content_id}' and '{root_folder_id}' in parents "
        "and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    existing = (
        svc.files()
        .list(q=q, spaces="drive", fields="files(id)")
        .execute()
        .get("files", [])
    )
    if existing:
        folder_id = existing[0]["id"]
    else:
        meta = {
            "name": content_id,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [root_folder_id],
        }
        folder_id = svc.files().create(body=meta, fields="id").execute()["id"]

    for local in paths:
        local = Path(local).resolve()
        if not local.is_file():
            raise FileNotFoundError(local)

        media = MediaFileUpload(str(local), resumable=True)
        file_meta = {"name": local.name, "parents": [folder_id]}
        uploaded = (
            svc.files()
            .create(body=file_meta, media_body=media, fields="id")
            .execute()
        )
        file_id = uploaded["id"]

        # Read-back verification
        request = svc.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        remote_sha = hashlib.sha256(buf.getvalue()).hexdigest()
        if remote_sha != _sha256(local):
            raise RuntimeError(f"Drive read-back mismatch for {local.name}")

    return True


if __name__ == "__main__":
    # Smoke test: python drive_verifier.py content_id file1 [file2 ...]
    import sys

    if len(sys.argv) < 3:
        print("Usage: drive_verifier.py <content_id> <file> [file ...]", file=sys.stderr)
        sys.exit(2)
    cid = sys.argv[1]
    files = [Path(p) for p in sys.argv[2:]]
    ok = drive_verifier(cid, files)
    print("True" if ok is True else repr(ok))
