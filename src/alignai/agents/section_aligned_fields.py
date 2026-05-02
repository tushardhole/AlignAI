"""Structured LLM output for single-section alignment."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SectionAlignedFields(BaseModel):
    """Aligned body for one resume section."""

    model_config = ConfigDict(frozen=True)

    aligned_content: str = Field(description="Rewritten section text tailored to the job")
