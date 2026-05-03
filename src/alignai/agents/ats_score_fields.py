"""Structured LLM output for ATS score."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_int, find_value


class AtsScoreFields(BaseModel):
    """ATS-oriented score."""

    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=1, le=100, description="ATS compatibility 1-100")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        hit = find_value(
            data,
            "score",
            "ats_score",
            "atsScore",
            "AtsScore",
            "compatibility_score",
            "compatibilityScore",
            "ats_compatibility",
            "value",
            "rating",
            "result",
        )
        if hit is not None:
            return {"score": coerce_int(hit, 1, 100)}
        for v in data.values():
            if isinstance(v, (int, float)):
                return {"score": coerce_int(v, 1, 100)}
        return data
