"""Core domain entities, value objects, and enums for AlignAI.

All types are pure Python (dataclasses or Pydantic) with zero I/O.
Domain entities use @dataclass(frozen=True); LLM output boundaries use
Pydantic v2 models with explicit model_config as required by CLAUDE.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, NewType

from pydantic import BaseModel, ConfigDict, field_validator

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

AlignmentId = NewType("AlignmentId", str)


class MatchLabel(StrEnum):
    """Rating label produced by the MatchScorer agent."""

    STRONG_MATCH = "Strong Match"
    GOOD_MATCH = "Good Match"
    FAIR_MATCH = "Fair Match"
    WEAK_MATCH = "Weak Match"
    POOR_MATCH = "Poor Match"


@dataclass(frozen=True)
class ResumeSection:
    """A single structural section of a resume (e.g. Experience, Education)."""

    heading: str
    content: str


@dataclass(frozen=True)
class ParsedResume:
    """Result of structurally parsing a resume into ordered sections."""

    resume_id: str
    sections: tuple[ResumeSection, ...]


@dataclass(frozen=True)
class Resume:
    """Base resume document uploaded by the user."""

    id: str
    content: str
    file_path: Path | None = None
    sections: tuple[ResumeSection, ...] | None = None


@dataclass(frozen=True)
class CoverLetter:
    """Base cover letter document uploaded by the user."""

    id: str
    content: str
    file_path: Path | None = None


@dataclass(frozen=True)
class JobPosting:
    """A job description successfully fetched or pasted by the user."""

    url: str
    title: str
    description: str
    source: str = "url"  # "url" | "pasted"


@dataclass(frozen=True)
class UnreadableJob:
    """Returned when a job page cannot be scraped by any strategy."""

    url: str
    reason: str


@dataclass(frozen=True)
class AtsScore:
    """ATS compatibility score in the inclusive range [1, 100]."""

    value: int

    def __post_init__(self) -> None:
        if not (1 <= self.value <= 100):
            raise ValueError(f"AtsScore must be 1-100, got {self.value}")


@dataclass(frozen=True)
class MatchScore:
    """Job-fit match score in the inclusive range [1, 5]."""

    value: int

    def __post_init__(self) -> None:
        if not (1 <= self.value <= 5):
            raise ValueError(f"MatchScore must be 1-5, got {self.value}")


@dataclass(frozen=True)
class AlignedResume:
    """Resume content tailored to a specific job posting."""

    content: str
    file_path: Path | None = None


@dataclass(frozen=True)
class AlignedCoverLetter:
    """Cover letter content tailored to a specific job posting."""

    content: str
    file_path: Path | None = None


@dataclass(frozen=True)
class Alignment:
    """Aggregate root representing one completed alignment run."""

    id: AlignmentId
    job_posting: JobPosting
    aligned_resume: AlignedResume
    aligned_cover_letter: AlignedCoverLetter
    ats_score: AtsScore
    match_score: MatchScore
    match_label: MatchLabel
    created_at: datetime


@dataclass(frozen=True)
class AlignmentInputs:
    """Inputs passed to the AgentRunner to start an alignment pipeline."""

    resume: Resume
    cover_letter: CoverLetter
    job_posting: JobPosting


class AlignmentResult(BaseModel):
    """Structured output returned from the AgentRunner (LLM I/O boundary)."""

    model_config = ConfigDict(frozen=True, use_enum_values=False)

    aligned_resume_content: str
    aligned_cover_letter_content: str
    ats_score: int
    match_score: int
    match_label: MatchLabel

    @field_validator("ats_score")
    @classmethod
    def validate_ats_score(cls, v: int) -> int:
        if not (1 <= v <= 100):
            raise ValueError(f"ats_score must be 1-100, got {v}")
        return v

    @field_validator("match_score")
    @classmethod
    def validate_match_score(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError(f"match_score must be 1-5, got {v}")
        return v
