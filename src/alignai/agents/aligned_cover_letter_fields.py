"""Structured LLM output for aligned cover letter."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AlignedCoverLetterFields(BaseModel):
    """Aligned cover letter output."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Tailored cover letter body")
