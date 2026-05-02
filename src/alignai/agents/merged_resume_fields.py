"""Structured LLM output for merged resume."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MergedResumeFields(BaseModel):
    """Final stitched resume after chunked alignment."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Full resume text with consistent tone")
