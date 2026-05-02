"""OS keyring accessors for API tokens."""

from __future__ import annotations

import contextlib

import keyring
import keyring.errors

_SERVICE = "AlignAI"


class KeyringSecrets:
    """Stores sensitive strings in the platform credential store."""

    def __init__(self, service_name: str = _SERVICE) -> None:
        self._service = service_name

    def get(self, key: str) -> str | None:
        try:
            val = keyring.get_password(self._service, key)
        except (RuntimeError, OSError):
            return None
        return val

    def set(self, key: str, value: str) -> None:
        keyring.set_password(self._service, key, value)

    def delete(self, key: str) -> None:
        with contextlib.suppress(keyring.errors.PasswordDeleteError):
            keyring.delete_password(self._service, key)
