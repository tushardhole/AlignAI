"""Structured LLM output for resume parsing."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResumeSectionFields(BaseModel):
    """One structural section of a resume."""

    model_config = ConfigDict(frozen=True)

    heading: str = Field(description="Section heading, e.g. Experience")
    content: str = Field(description="Verbatim section body")


class ParsedResumeFields(BaseModel):
    """Ordered resume sections from ResumeParserAgent."""

    model_config = ConfigDict(frozen=True)

    sections: list[ResumeSectionFields] = Field(
        description="Ordered sections from top to bottom",
    )
