"""Resolved application directories (config + data)."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


def resolve_config_dir() -> Path:
    """User-writable directory for non-secret JSON settings."""
    return Path(user_config_dir("AlignAI", appauthor=False))


def resolve_data_dir() -> Path:
    """User-writable directory for SQLite DB, PDFs, and cached documents."""
    return Path(user_data_dir("AlignAI", appauthor=False))
