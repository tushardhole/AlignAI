"""Persist and load the user's base resume and cover letter."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from alignai.domain.models import CoverLetter, Resume
from alignai.domain.ports import SettingsStore
from alignai.infra.pdf_input_pypdf import PdfDocxTextExtractor


class FilesystemDocumentRepository:
    """Stores base documents under the app data directory."""

    def __init__(
        self,
        data_dir: Path,
        settings: SettingsStore,
        extractor: PdfDocxTextExtractor,
    ) -> None:
        self._root = data_dir / "base_documents"
        self._root.mkdir(parents=True, exist_ok=True)
        self._settings = settings
        self._extractor = extractor

    def get_resume(self) -> Resume | None:
        path_str = self._settings.get("base_resume_path")
        if not path_str:
            return None
        path = Path(path_str)
        if not path.exists():
            return None
        content = self._extractor.extract(path)
        return Resume(id="base_resume", content=content, file_path=path)

    def save_resume(self, resume: Resume) -> None:
        if resume.file_path is None:
            raise ValueError("resume.file_path is required to persist")
        dest = self._copy_into_store(resume.file_path, prefix="resume")
        self._settings.set("base_resume_path", str(dest))

    def get_cover_letter(self) -> CoverLetter | None:
        path_str = self._settings.get("base_cover_letter_path")
        if not path_str:
            return None
        path = Path(path_str)
        if not path.exists():
            return None
        content = self._extractor.extract(path)
        return CoverLetter(id="base_cover", content=content, file_path=path)

    def save_cover_letter(self, cover_letter: CoverLetter) -> None:
        if cover_letter.file_path is None:
            raise ValueError("cover_letter.file_path is required to persist")
        dest = self._copy_into_store(cover_letter.file_path, prefix="cover")
        self._settings.set("base_cover_letter_path", str(dest))

    def _copy_into_store(self, source: Path, prefix: str) -> Path:
        suffix = source.suffix.lower() or ".pdf"
        dest = self._root / f"{prefix}_{uuid.uuid4().hex}{suffix}"
        shutil.copy2(source, dest)
        return dest
