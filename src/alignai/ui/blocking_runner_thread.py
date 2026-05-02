"""Qt thread wrapper for blocking workers (e.g. Telegram long-poll)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThread


class BlockingRunnerThread(QThread):
    """Runs a blocking callable on a worker thread."""

    def __init__(self, fn: Callable[[], None]) -> None:
        super().__init__()
        self._fn = fn

    def run(self) -> None:
        self._fn()
