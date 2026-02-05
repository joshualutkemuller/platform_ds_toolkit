
import json, logging, os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from .key_manager import load_key

logger = logging.getLogger(__name__)

def _default_root() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".platform_ds_toolkit"
    return Path.home() / ".platform_ds_toolkit"

DEFAULT_VAULT_PATH = _default_root() / "credentials.enc"

class CredentialVault:
    def __init__(self, vault_path: Path = DEFAULT_VAULT_PATH):
        self.vault_path = vault_path
        self.fernet = Fernet(load_key())

    def _load(self) -> Dict[str, Any]:
        if not self.vault_path.exists():
            return {}
        return json.loads(self.fernet.decrypt(self.vault_path.read_bytes()).decode())

    def _write(self, data: Dict[str, Any]) -> None:
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.vault_path.write_bytes(self.fernet.encrypt(json.dumps(data, indent=2).encode()))

    def save_credentials(self, path: str, secrets: Dict[str, str], metadata: Optional[Dict[str, Any]] = None):
        data = self._load()
        data[path] = {
            "secrets": secrets,
            "metadata": {"created_at": datetime.utcnow().isoformat(), **(metadata or {})},
        }
        self._write(data)

    def load_credentials(self, path: str) -> Dict[str, str]:
        data = self._load()
        if path not in data:
            raise ValueError(f"No credentials for {path}")
        return data[path]["secrets"]

    def list_paths(self):
        return sorted(self._load().keys())
