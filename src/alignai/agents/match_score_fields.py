"""Structured LLM output for match score."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_int, coerce_match_label, find_value
from alignai.domain.models import MatchLabel


class MatchScoreFields(BaseModel):
    """Fit score plus categorical label."""

    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=1, le=5, description="Overall fit score 1-5")
    label: MatchLabel = Field(description="Human-readable bucket")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        score_val = find_value(
            data,
            "score",
            "match_score",
            "matchScore",
            "fit_score",
            "fitScore",
            "rating",
            "value",
            "overall_score",
        )
        score = coerce_int(score_val, 1, 5) if score_val is not None else 3
        # Always derive label from numeric score — LLM label text is unreliable
        label = coerce_match_label("", score)
        return {"score": score, "label": label}
