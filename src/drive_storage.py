"""Local immutable output helpers and an explicit real Drive upload/readback adapter.

Local saves alone remain drafts. DriveVerifier requires actual machine credentials.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import OUTPUT_PATH, ensure_dirs
from .safety import content_id as valid_content, confined
from .ledger import storage_lock


def save_text(
    content_id: str,
    filename: str,
    text: str,
    *,
    subfolder: str = "",
) -> Path:
    ensure_dirs()
    folder = confined(OUTPUT_PATH, valid_content(content_id))
    if subfolder:
        folder = confined(folder, subfolder)
    folder.mkdir(parents=True, exist_ok=True)
    path = confined(folder, filename)
    with storage_lock():
        if path.exists():
            if path.read_text(encoding="utf-8") != text:
                raise FileExistsError("Existing output differs; preserve it and review revisions explicitly")
        else:
            with path.open("x", encoding="utf-8") as f:
                f.write(text)
    return path


def list_outputs(content_id: str) -> list[Path]:
    folder = confined(OUTPUT_PATH, valid_content(content_id))
    if not folder.exists():
        return []
    return sorted(p for p in folder.rglob("*") if p.is_file())


def drive_placeholder_meta(local_path: Path, intended_drive_folder: str) -> dict[str, Any]:
    """Record where this should live in Drive once credentials are wired."""
    return {
        "local_path": str(local_path),
        "intended_drive_folder": intended_drive_folder,
        "uploaded": False,
        "note": "Wire google-api-python-client when ready; keep open-stack rules.",
    }


class DriveVerifier:
    """Upload once per identity/name; verify provider bytes before recording success.

    Use a machine-owned OAuth access token. The caller never gives this object to
    Hermes. Identical retries reuse remote files; conflicts are never overwritten.
    """
    def __init__(self, folder_id, token, *, session=None):
        import re
        import requests
        if not isinstance(folder_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', folder_id) or not token:
            raise RuntimeError('Drive folder ID and OAuth access token required')
        self.folder_id = folder_id
        self.session = session or requests.Session()
        self.session.trust_env = False
        self.session.headers.update({'Authorization': 'Bearer ' + token})
        self.receipts = []

    def close(self):
        self.session.close()

    def request(self, method, url, **kwargs):
        response = getattr(self.session, method)(url, timeout=(5, 60), allow_redirects=False, **kwargs)
        if response.status_code != 200:
            raise RuntimeError(f'Drive {method} failed: HTTP {response.status_code}')
        return response

    def __call__(self, identity, files):
        import hashlib
        import json
        import re
        import uuid
        if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', identity):
            raise ValueError('Invalid Drive identity')
        files = list(map(Path, files))
        if not files or len({p.name for p in files}) != len(files):
            raise ValueError('Drive files must have unique names')
        for path in files:
            data = path.read_bytes()
            if not data: raise RuntimeError('Empty Drive artifact')
            digest = hashlib.sha256(data).hexdigest()
            # Filenames originate in validated local output; quote Drive query literals.
            name = path.name.replace('\\', '\\\\').replace("'", "\\'")
            query = (f"'{self.folder_id}' in parents and trashed = false and name = '{name}' "
                     f"and appProperties has {{ key='reboot_identity' and value='{identity}' }}")
            result = self.request('get', 'https://www.googleapis.com/drive/v3/files',
                                  params={'q':query, 'fields':'files(id,name,parents,appProperties),nextPageToken', 'pageSize':100}).json()
            matches = result.get('files')
            if not isinstance(matches,list) or len(matches)>1 or result.get('nextPageToken'):
                raise RuntimeError('Ambiguous Drive identity')
            expected = dict(reboot_identity=identity,sha256=digest)
            if matches:
                meta = matches[0]
            else:
                boundary = 'reboot_' + uuid.uuid4().hex
                meta = dict(name=path.name, parents=[self.folder_id],appProperties=expected)
                payload = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'.encode()
                           + json.dumps(meta).encode() + f'\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
                           + data + f'\r\n--{boundary}--\r\n'.encode())
                meta = self.request('post','https://www.googleapis.com/upload/drive/v3/files',
                                    params={'uploadType':'multipart','fields':'id,name,parents,appProperties'},
                                    data=payload,headers={'Content-Type':f'multipart/related; boundary={boundary}'}).json()
            if (meta.get('name') != path.name or meta.get('parents') != [self.folder_id]
                    or meta.get('appProperties') != expected or not re.fullmatch(r'[A-Za-z0-9_-]+',meta.get('id',''))):
                raise RuntimeError('Drive identity/hash conflict; remote file preserved')
            returned = self.request('get',f'https://www.googleapis.com/drive/v3/files/{meta["id"]}',params={'alt':'media'}).content
            if hashlib.sha256(returned).hexdigest() != digest:
                raise RuntimeError('Drive readback hash mismatch')
            self.receipts.append(dict(identity=identity,name=path.name,file_id=meta['id'],sha256=digest,parent=self.folder_id))
        return True
