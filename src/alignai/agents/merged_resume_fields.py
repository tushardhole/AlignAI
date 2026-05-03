"""Structured LLM output for merged resume."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, find_value


class MergedResumeFields(BaseModel):
    """Final stitched resume after chunked alignment."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Full resume text with consistent tone")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        hit = find_value(
            data,
            "content",
            "resume",
            "merged_resume",
            "mergedResume",
            "final_resume",
            "text",
            "body",
            "output",
            "result",
        )
        if hit is not None:
            return {"content": coerce_str(hit).strip()}
        items = list(data.items())
        if len(items) == 1:
            return {"content": coerce_str(items[0][1]).strip()}
        # Multi-key semantic resume dict: flatten everything to text
        return {"content": coerce_str(data).strip()}
