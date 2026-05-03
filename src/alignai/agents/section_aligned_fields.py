"""Structured LLM output for single-section alignment."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, find_value


def _format_section_content(value: Any) -> str:
    """Format a section value: lists become bullet points, other values flatten to text."""
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            if isinstance(item, dict):
                text_vals = [str(v) for v in item.values() if isinstance(v, str) and v]
                lines.append("- " + ", ".join(text_vals) if text_vals else "- " + coerce_str(item))
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)
    return coerce_str(value)


class SectionAlignedFields(BaseModel):
    """Aligned body for one resume section."""

    model_config = ConfigDict(frozen=True)

    aligned_content: str = Field(
        description="Rewritten section text tailored to the job",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        hit = find_value(
            data,
            "aligned_content",
            "alignedContent",
            "content",
            "text",
            "body",
            "rewritten_content",
            "rewrittenContent",
            "section_content",
            "output",
            "result",
        )
        if hit is not None:
            return {"aligned_content": _format_section_content(hit).strip()}
        items = list(data.items())
        if len(items) == 1:
            return {"aligned_content": _format_section_content(items[0][1]).strip()}
        vals = [_format_section_content(v).strip() for v in data.values() if v]
        if vals:
            return {"aligned_content": "\n\n".join(vals)}
        return data
