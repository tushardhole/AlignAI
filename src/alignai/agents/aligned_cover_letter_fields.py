"""Structured LLM output for aligned cover letter."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, find_value


class AlignedCoverLetterFields(BaseModel):
    """Aligned cover letter output."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(description="Tailored cover letter body")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        hit = find_value(
            data,
            "content",
            "cover_letter",
            "coverLetter",
            "letter",
            "body",
            "text",
            "aligned_cover_letter",
            "alignedCoverLetter",
            "output",
            "result",
            "response",
        )
        if hit is not None:
            return {"content": coerce_str(hit).strip()}
        items = list(data.items())
        if len(items) == 1:
            return {"content": coerce_str(items[0][1]).strip()}
        return {"content": coerce_str(data).strip()}
