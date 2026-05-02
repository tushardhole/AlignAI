"""Non-secret settings persisted as JSON under the application config directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


class JsonSettingsStore:
    """Reads and writes string key/value pairs in a JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: str | None = None) -> str | None:
        data = self._load()
        if key not in data:
            return default
        val = data[key]
        if val is None:
            return default
        return str(val)

    def set(self, key: str, value: str) -> None:
        data = self._load()
        data[key] = value
        self._save(data)

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        raw = self._path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return cast(dict[str, Any], data)

    def _save(self, data: dict[str, Any]) -> None:
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self._path)
