from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import json
import joblib


class ModelStore:
    """
    Filesystem-based model artifact store.

    Layout:
        model_store/
            model_name/
                v1/
                    model.joblib
                    manifest.json
                v2/
                    ...
    """

    def __init__(self, root: Path, read_only: bool = False):
        self.root = root
        self.read_only = read_only
        self.root.mkdir(parents=True, exist_ok=True)

    # ---------- public API ----------

    def save(
        self,
        name: str,
        model: Any,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """
        Save a trained model artifact.

        Parameters
        ----------
        name : str
            Logical model name (e.g. "specials_classifier")
        model : Any
            Trained model object (must be joblib-serializable)
        version : str, optional
            Version label (defaults to auto-increment vN)
        metadata : dict, optional
            Arbitrary metadata (features, horizon, params, etc.)
        """
        if self.read_only:
            raise PermissionError("ModelStore is in read-only mode")

        version = version or self._next_version(name)
        path = self.root / name / version
        path.mkdir(parents=True, exist_ok=True)

        # Save model
        joblib.dump(model, path / "model.joblib")

        # Save manifest
        manifest = {
            "artifact_type": "model",
            "name": name,
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        (path / "manifest.json").write_text(
            json.dumps(manifest, indent=2)
        )

        return path

    def load(self, name: str, version: str = "latest") -> Any:
        """
        Load a model artifact.
        """
        path = self._resolve_version(name, version)
        return joblib.load(path / "model.joblib")

    def info(self, name: str, version: str = "latest") -> Dict[str, Any]:
        """
        Load manifest metadata without loading the model.
        """
        path = self._resolve_version(name, version)
        return json.loads((path / "manifest.json").read_text())

    def list_models(self) -> list[str]:
        """
        List all stored model names.
        """
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def list_versions(self, name: str) -> list[str]:
        """
        List versions for a given model.
        """
        base = self.root / name
        if not base.exists():
            return []
        return sorted(p.name for p in base.iterdir() if p.is_dir())

    # ---------- helpers ----------

    def _next_version(self, name: str) -> str:
        base = self.root / name
        if not base.exists():
            return "v1"

        versions = self.list_versions(name)
        nums = [int(v[1:]) for v in versions if v.startswith("v")]
        return f"v{max(nums) + 1}"

    def _resolve_version(self, name: str, version: str) -> Path:
        base = self.root / name
        if not base.exists():
            raise ValueError(f"No model named '{name}' found")

        if version == "latest":
            versions = self.list_versions(name)
            if not versions:
                raise ValueError(f"No versions found for model '{name}'")
            version = versions[-1]

        path = base / version
        if not path.exists():
            raise ValueError(f"Model '{name}/{version}' not found")

        return path
