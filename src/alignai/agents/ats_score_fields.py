"""Structured LLM output for ATS score."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AtsScoreFields(BaseModel):
    """ATS-oriented score."""

    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=1, le=100, description="ATS compatibility 1-100")
