"""Minimal PDF renderer for tests (writes placeholder bytes)."""

from __future__ import annotations

from pathlib import Path


class RecordingPdfRenderer:
    """Records HTML inputs and writes minimal PDF-shaped bytes."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Path]] = []

    async def render(self, html: str, output_path: Path) -> Path:
        self.calls.append((html, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"%PDF-1.4\n%minimal test fixture\n")
        return output_path
