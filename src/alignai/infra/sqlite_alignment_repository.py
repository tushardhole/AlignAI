"""SQLite persistence for completed alignments."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from alignai.domain.models import (
    AlignedCoverLetter,
    AlignedResume,
    Alignment,
    AlignmentId,
    AtsScore,
    JobPosting,
    MatchScore,
    label_from_score,
)


class SqliteAlignmentRepository:
    """Stores alignment rows in a local SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alignments (
                    id TEXT PRIMARY KEY,
                    job_url TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    job_description TEXT NOT NULL,
                    job_source TEXT NOT NULL,
                    aligned_resume_path TEXT NOT NULL,
                    aligned_cover_path TEXT NOT NULL,
                    aligned_resume_content TEXT NOT NULL,
                    aligned_cover_content TEXT NOT NULL,
                    ats_score INTEGER NOT NULL,
                    match_score INTEGER NOT NULL,
                    match_label TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, alignment: Alignment) -> AlignmentId:
        created_iso = alignment.created_at.astimezone(UTC).isoformat()
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO alignments (
                    id, job_url, job_title, job_description, job_source,
                    aligned_resume_path, aligned_cover_path,
                    aligned_resume_content, aligned_cover_content,
                    ats_score, match_score, match_label, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(alignment.id),
                    alignment.job_posting.url,
                    alignment.job_posting.title,
                    alignment.job_posting.description,
                    alignment.job_posting.source,
                    str(alignment.aligned_resume.file_path or ""),
                    str(alignment.aligned_cover_letter.file_path or ""),
                    alignment.aligned_resume.content,
                    alignment.aligned_cover_letter.content,
                    alignment.ats_score.value,
                    alignment.match_score.value,
                    alignment.match_label.value,
                    created_iso,
                ),
            )
            conn.commit()
        return alignment.id

    def list(self) -> list[Alignment]:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM alignments ORDER BY created_at DESC").fetchall()
        return [self._row_to_alignment(dict(row)) for row in rows]

    def get(self, alignment_id: AlignmentId) -> Alignment | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM alignments WHERE id = ?",
                (str(alignment_id),),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_alignment(dict(row))

    def _row_to_alignment(self, row: dict[str, object]) -> Alignment:
        jp = JobPosting(
            url=str(row["job_url"]),
            title=str(row["job_title"]),
            description=str(row["job_description"]),
            source=str(row["job_source"]),
        )
        resume_path = str(row["aligned_resume_path"])
        cover_path = str(row["aligned_cover_path"])
        aligned_resume = AlignedResume(
            content=str(row["aligned_resume_content"]),
            file_path=Path(resume_path) if resume_path else None,
        )
        aligned_cover = AlignedCoverLetter(
            content=str(row["aligned_cover_content"]),
            file_path=Path(cover_path) if cover_path else None,
        )
        created_raw = str(row["created_at"])
        created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        match_score = MatchScore(int(str(row["match_score"])))
        return Alignment(
            id=AlignmentId(str(row["id"])),
            job_posting=jp,
            aligned_resume=aligned_resume,
            aligned_cover_letter=aligned_cover,
            ats_score=AtsScore(int(str(row["ats_score"]))),
            match_score=match_score,
            match_label=label_from_score(match_score.value),
            created_at=created,
        )
