"""AlignAI — AI-powered resume and cover-letter aligner."""

from __future__ import annotations

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__: str = version("alignai")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"
