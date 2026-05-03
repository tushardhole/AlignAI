"""Pydantic model for LLM-structured cover letter JSON output."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, coerce_str_list, find_value


class StructuredCoverLetterFields(BaseModel):
    """Cover letter structured into template-ready JSON by the structuring agent."""

    model_config = ConfigDict(frozen=True)

    candidate_name: str = Field(default="")
    paragraphs: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        return _normalize_cover_letter_dict(data)


def _normalize_cover_letter_dict(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize LLM output into canonical cover letter schema."""
    name = find_value(
        raw,
        "candidate_name",
        "candidateName",
        "name",
        "contact_name",
        "contactName",
        "author",
    )
    candidate_name = coerce_str(name).strip() if name else ""

    paragraphs = _extract_paragraphs(raw)

    return {"candidate_name": candidate_name, "paragraphs": paragraphs}


def _extract_paragraphs(raw: dict[str, Any]) -> list[str]:
    """Extract body paragraphs from various LLM output shapes."""
    hit = find_value(
        raw,
        "paragraphs",
        "body_paragraphs",
        "bodyParagraphs",
        "sections",
    )
    if isinstance(hit, list):
        return [coerce_str(p).strip() for p in hit if p]

    body = find_value(
        raw,
        "body",
        "content",
        "text",
        "letter",
        "cover_letter",
    )
    if body:
        return _split_into_paragraphs(coerce_str(body))

    vals = [v for v in raw.values() if isinstance(v, str) and len(v) > 80]
    if vals:
        longest = max(vals, key=len)
        return _split_into_paragraphs(longest)

    items = coerce_str_list(raw)
    if items:
        return [p for p in items if len(p) > 30]
    return []


def _split_into_paragraphs(text: str) -> list[str]:
    """Split continuous text into paragraphs, stripping greeting/closing."""
    _GREETING_RE = re.compile(r"^(Dear\b.*?[,:]?)\s*$", re.IGNORECASE)
    _CLOSING_RE = re.compile(
        r"^(Regards|Sincerely|Best regards|Thank you|Yours truly|Respectfully)\b",
        re.IGNORECASE,
    )

    paragraphs: list[str] = []
    current = ""

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(current.strip())
                current = ""
            continue
        if _GREETING_RE.match(stripped):
            continue
        if _CLOSING_RE.match(stripped):
            if current:
                paragraphs.append(current.strip())
            break
        current = f"{current} {stripped}" if current else stripped

    if current:
        paragraphs.append(current.strip())

    return [p for p in paragraphs if len(p) > 30]
