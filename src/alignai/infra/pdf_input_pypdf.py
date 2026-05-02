"""Extract plain text from PDF and DOCX uploads."""

from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class PdfDocxTextExtractor:
    """Reads UTF-8 text from PDF or DOCX files."""

    def extract(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._read_pdf(path)
        if suffix in {".docx", ".doc"}:
            return self._read_docx(path)
        raise ValueError(f"Unsupported document type: {suffix}")

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    def _read_docx(self, path: Path) -> str:
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
