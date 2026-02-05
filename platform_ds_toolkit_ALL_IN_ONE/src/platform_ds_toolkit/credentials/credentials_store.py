"""
credentials_store.py

A small, dependency-free credential store that persists records to a JSON file.

Design goals:
- Store arbitrary custom fields per credential (username, password, token, notes, etc.)
- Ensure backing file + parent directory exist
- Safe(ish) writes via atomic replace (write temp -> fsync -> replace)
- Simple CRUD: upsert, get, list, delete
- Optional environment-variable expansion in file path (e.g., %USERPROFILE% on Windows)

Security note:
- This stores secrets in *plain text* JSON. Use OS keychain / vault or add encryption if needed.
"""

from __future__ import annotations

import json
import os
import time
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class CredentialStoreError(Exception):
    """Base error for credential store."""


class CredentialNotFoundError(CredentialStoreError):
    """Raised when a credential key is not found."""


class CredentialExistsError(CredentialStoreError):
    """Raised when a credential key already exists and overwrite=False."""


class CorruptStoreError(CredentialStoreError):
    """Raised when the JSON store cannot be parsed."""


@dataclass(frozen=True)
class StoreConfig:
    """
    file_path: Path to JSON file.
    auto_create: If True, creates file + parent directory if missing.
    """
    file_path: Path
    auto_create: bool = True


def default_store_path(app_name: str = "platform_ds_toolkit") -> Path:
    """
    Returns a sensible default path:
    - Windows: %USERPROFILE%\\.<app_name>\\credentials.json
    - Mac/Linux: ~/.<app_name>/credentials.json
    """
    home = Path.home()
    return home / f".{app_name}" / "credentials.json"


def _expand_path(p: str | Path) -> Path:
    # Expand ~ and environment variables
    s = str(p)
    s = os.path.expandvars(s)
    return Path(s).expanduser().resolve()


def _now_ts() -> float:
    return time.time()


def _ensure_file_exists(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"_meta": {"created_at": _now_ts()}, "credentials": {}}, indent=2))


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        raise CorruptStoreError(f"Credential store JSON is corrupt: {path}") from e

    # Normalize structure
    if not isinstance(data, dict):
        raise CorruptStoreError(f"Credential store JSON root must be an object: {path}")

    data.setdefault("_meta", {})
    data.setdefault("credentials", {})

    if not isinstance(data["credentials"], dict):
        raise CorruptStoreError(f"'credentials' must be an object/dict in store: {path}")

    return data


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """
    Atomic-ish write: write to temp file in same directory, fsync, then replace.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True)

    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)  # atomic on most OS/filesystems
    finally:
        # If replace failed, try cleanup
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except OSError:
            pass


class CredentialStore:
    """
    JSON-backed store of credential "records".

    Each record:
      - key: string identifier you choose (e.g., "snowflake/prod", "factset", "gmail")
      - fields: arbitrary dict you provide (e.g., {"username": "...", "password": "...", "role": "..."} )
      - system fields: created_at, updated_at
    """

    def __init__(self, config: StoreConfig):
        self.path = _expand_path(config.file_path)
        self.auto_create = config.auto_create
        if self.auto_create:
            _ensure_file_exists(self.path)
        elif not self.path.exists():
            raise FileNotFoundError(f"Credential store file does not exist: {self.path}")

    @classmethod
    def from_default(cls, app_name: str = "platform_ds_toolkit", auto_create: bool = True) -> "CredentialStore":
        return cls(StoreConfig(file_path=default_store_path(app_name), auto_create=auto_create))

    def exists(self) -> bool:
        return self.path.exists()

    def ensure_exists(self) -> None:
        _ensure_file_exists(self.path)

    def _read_store(self) -> Dict[str, Any]:
        if not self.path.exists():
            if self.auto_create:
                _ensure_file_exists(self.path)
            else:
                raise FileNotFoundError(f"Credential store file does not exist: {self.path}")
        return _load_json(self.path)

    def _write_store(self, store: Dict[str, Any]) -> None:
        _atomic_write_json(self.path, store)

    def list_keys(self) -> List[str]:
        store = self._read_store()
        return sorted(store["credentials"].keys())

    def has(self, key: str) -> bool:
        store = self._read_store()
        return key in store["credentials"]

    def get(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        store = self._read_store()
        rec = store["credentials"].get(key)
        if rec is None:
            return default
        # Return a copy so callers don't mutate internal data accidentally
        return json.loads(json.dumps(rec))

    def require(self, key: str) -> Dict[str, Any]:
        rec = self.get(key)
        if rec is None:
            raise CredentialNotFoundError(f"Credential '{key}' not found in {self.path}")
        return rec

    def upsert(self, key: str, fields: Dict[str, Any], overwrite: bool = True) -> Dict[str, Any]:
        """
        Create or update a credential record.
        - fields can be any JSON-serializable dict
        - if overwrite=False and key exists -> CredentialExistsError
        Returns the stored record.
        """
        if not isinstance(fields, dict):
            raise ValueError("fields must be a dict")

        store = self._read_store()
        creds = store["credentials"]

        now = _now_ts()
        if key in creds and not overwrite:
            raise CredentialExistsError(f"Credential '{key}' already exists (overwrite=False).")

        existing = creds.get(key, {})
        created_at = existing.get("created_at", now)

        record = {
            "created_at": created_at,
            "updated_at": now,
            "fields": fields,
        }

        # Ensure JSON-serializable (fail fast)
        try:
            json.dumps(record)
        except TypeError as e:
            raise ValueError("fields contains non-JSON-serializable values") from e

        creds[key] = record
        store["_meta"]["updated_at"] = now
        self._write_store(store)
        return self.get(key)  # return a clean copy

    def delete(self, key: str, missing_ok: bool = False) -> None:
        store = self._read_store()
        creds = store["credentials"]
        if key not in creds:
            if missing_ok:
                return
            raise CredentialNotFoundError(f"Credential '{key}' not found.")
        del creds[key]
        store["_meta"]["updated_at"] = _now_ts()
        self._write_store(store)

    def update_fields(self, key: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge patch dict into existing fields (shallow merge).
        """
        rec = self.require(key)
        fields = rec.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}
        fields.update(patch)
        return self.upsert(key, fields, overwrite=True)


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    store = CredentialStore.from_default(app_name="platform_ds_toolkit")

    # Save credentials with custom fields
    store.upsert(
        "snowflake/prod",
        {
            "account": "myacct",
            "username": "josh",
            "password": "REDACTED",
            "role": "ANALYST",
            "warehouse": "WH_XL",
        },
        overwrite=True,
    )

    # Read them back
    rec = store.require("snowflake/prod")
    print("Fields:", rec["fields"])

    # List available credential keys
    print("Keys:", store.list_keys())

    # Patch/update a single field
    store.update_fields("snowflake/prod", {"warehouse": "WH_L"})
