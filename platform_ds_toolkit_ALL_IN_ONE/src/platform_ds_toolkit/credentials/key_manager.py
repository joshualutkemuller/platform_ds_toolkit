
from cryptography.fernet import Fernet
from pathlib import Path
import os

def _default_root() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".platform_ds_toolkit"
    return Path.home() / ".platform_ds_toolkit"

DEFAULT_KEY_PATH = _default_root() / "master.key"

def generate_key(key_path: Path = DEFAULT_KEY_PATH) -> None:
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        raise FileExistsError("Master key already exists")
    key_path.write_bytes(Fernet.generate_key())

def load_key(key_path: Path = DEFAULT_KEY_PATH) -> bytes:
    if not key_path.exists():
        raise FileNotFoundError("Encryption key not found; run generate_key()")
    return key_path.read_bytes()
