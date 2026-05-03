"""Background thread running one asyncio coroutine to completion."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from PySide6.QtCore import QThread, Signal


class AsyncRunnerThread(QThread):
    """Runs async code without blocking the Qt GUI thread."""

    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, coro: Coroutine[Any, Any, object]) -> None:
        super().__init__()
        self._coro = coro

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            out = loop.run_until_complete(self._coro)
            self.finished_ok.emit(out)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            loop.close()
