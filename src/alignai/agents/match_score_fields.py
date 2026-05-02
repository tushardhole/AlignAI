"""Structured LLM output for match score."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from alignai.domain.models import MatchLabel


class MatchScoreFields(BaseModel):
    """Fit score plus categorical label."""

    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=1, le=5, description="Overall fit score 1-5")
    label: MatchLabel = Field(description="Human-readable bucket")
