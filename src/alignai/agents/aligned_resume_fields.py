"""Structured LLM output for aligned resume (single-pass)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AlignedResumeFields(BaseModel):
    """Single-pass aligned resume output."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Full tailored resume in plain text")
