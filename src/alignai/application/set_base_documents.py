"""Use case: persist base resume and cover letter paths."""

from __future__ import annotations

from pathlib import Path

from alignai.domain.models import CoverLetter, Resume
from alignai.domain.ports import DocumentRepository


class SetBaseDocuments:
    """Copies user-selected files into the app data directory."""

    def __init__(self, documents: DocumentRepository) -> None:
        self._documents = documents

    def save_resume(self, source_path: Path) -> None:
        resume = Resume(id="base_resume", content="", file_path=source_path)
        self._documents.save_resume(resume)

    def save_cover_letter(self, source_path: Path) -> None:
        letter = CoverLetter(id="base_cover", content="", file_path=source_path)
        self._documents.save_cover_letter(letter)
