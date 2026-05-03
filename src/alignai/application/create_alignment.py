"""Use case: execute alignment pipeline and persist PDF artifacts."""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from alignai.application.pdf_markup import format_cover_letter_pdf_html, format_resume_pdf_html
from alignai.domain.models import (
    AlignedCoverLetter,
    AlignedResume,
    Alignment,
    AlignmentId,
    AlignmentInputs,
    AtsScore,
    MatchScore,
)
from alignai.domain.ports import AgentRunner, AlignmentRepository, PdfRenderer


def _extract_job_id(url: str) -> str:
    m = re.search(r"/jobs/view/(\d+)", url)
    if m:
        return m.group(1)
    parsed = urlparse(url)
    for key in ("jk", "job_id", "id", "jobId"):
        vals = parse_qs(parsed.query).get(key)
        if vals:
            return re.sub(r"[^\w\-]", "", vals[0])[:32]
    m = re.search(r"/(\d{4,})", url)
    if m:
        return m.group(1)
    return uuid.uuid4().hex[:8]


class CreateAlignment:
    """Orchestrates agent run, deterministic cleanup, PDF render, and SQLite save."""

    def __init__(
        self,
        runner: AgentRunner,
        alignment_repository: AlignmentRepository,
        pdf_renderer: PdfRenderer,
        output_root: Path,
        sanitize_text: Callable[[str], str],
    ) -> None:
        self._runner = runner
        self._alignment_repository = alignment_repository
        self._pdf_renderer = pdf_renderer
        self._output_root = output_root
        self._sanitize_text = sanitize_text

    async def execute(self, inputs: AlignmentInputs) -> Alignment:
        raw = await self._runner.run(inputs)
        resume_txt = self._sanitize_text(raw.aligned_resume_content)
        cover_txt = self._sanitize_text(raw.aligned_cover_letter_content)
        aid = AlignmentId(str(uuid.uuid4()))
        out_dir = self._output_root / "alignments" / str(aid)
        out_dir.mkdir(parents=True, exist_ok=True)
        job_id = _extract_job_id(inputs.job_posting.url)
        resume_pdf = out_dir / f"{job_id}_resume.pdf"
        cover_pdf = out_dir / f"{job_id}_cv.pdf"
        resume_html = format_resume_pdf_html("Aligned resume", resume_txt)
        cover_html = format_cover_letter_pdf_html("Aligned cover letter", cover_txt)
        await self._pdf_renderer.render(resume_html, resume_pdf)
        await self._pdf_renderer.render(cover_html, cover_pdf)
        entity = Alignment(
            id=aid,
            job_posting=inputs.job_posting,
            aligned_resume=AlignedResume(content=resume_txt, file_path=resume_pdf),
            aligned_cover_letter=AlignedCoverLetter(content=cover_txt, file_path=cover_pdf),
            ats_score=AtsScore(raw.ats_score),
            match_score=MatchScore(raw.match_score),
            match_label=raw.match_label,
            created_at=datetime.now(UTC),
        )
        self._alignment_repository.save(entity)
        return entity
