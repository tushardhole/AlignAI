"""Pytest fixtures shared across the suite."""

from __future__ import annotations

import threading
from collections.abc import Generator
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer
from typing import ClassVar

import pytest

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "job_pages"


class _RootedHandler(SimpleHTTPRequestHandler):
    """Serves a fixed directory (Python 3.7+ `directory` on the base class)."""

    base_dir: ClassVar[Path] = FIXTURE_ROOT

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(self.base_dir), **kwargs)


@pytest.fixture
def job_pages_http_server() -> Generator[str, None, None]:
    """Serve ``tests/fixtures/job_pages`` at ``http://127.0.0.1:<port>/``."""
    httpd = TCPServer(("127.0.0.1", 0), _RootedHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
