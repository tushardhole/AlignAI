"""Structured LLM output for resume parsing."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import (
    _norm_key,
    coerce_str,
    find_value,
)

# Maps normalised key → canonical section heading
_HEADING_MAP: dict[str, str] = {
    "name": "Contact",
    "contact": "Contact",
    "contact_info": "Contact",
    "contact_information": "Contact",
    "summary": "Summary",
    "objective": "Summary",
    "professional_summary": "Summary",
    "career_summary": "Summary",
    "experience": "Experience",
    "experiences": "Experience",
    "employment": "Experience",
    "work_experience": "Experience",
    "work_history": "Experience",
    "education": "Education",
    "skills": "Skills",
    "technical_skills": "Skills",
    "certifications": "Certifications",
    "certificates": "Certifications",
    "projects": "Projects",
    "achievements": "Achievements",
    "open_source_contributions": "Open Source",
    "open_source": "Open Source",
}


def _canonical_heading(key: str) -> str:
    return _HEADING_MAP.get(_norm_key(key), key.strip().replace("_", " "))


def _dict_to_sections(data: dict[str, Any]) -> list[dict[str, str]]:
    """Convert any resume-shaped dict into [{heading, content}] sections."""
    sections: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    for key, value in data.items():
        if value is None or value == "" or value == [] or value == {}:
            continue
        heading = _canonical_heading(key)
        content = coerce_str(value).strip()
        if not content:
            continue
        if heading in seen:
            sections[seen[heading]]["content"] += "\n" + content
        else:
            seen[heading] = len(sections)
            sections.append({"heading": heading, "content": content})
    return sections


class ResumeSectionFields(BaseModel):
    """One structural section of a resume."""

    model_config = ConfigDict(frozen=True)

    heading: str = Field(description="Section heading, e.g. Experience")
    content: str = Field(description="Verbatim section body")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        heading = find_value(
            data,
            "heading",
            "title",
            "name",
            "header",
            "section_heading",
            "section_name",
            "section_title",
        )
        content = find_value(
            data,
            "content",
            "body",
            "text",
            "section_content",
            "details",
            "description",
        )
        if heading is not None and content is not None:
            return {"heading": coerce_str(heading), "content": coerce_str(content)}
        return data


class ParsedResumeFields(BaseModel):
    """Ordered resume sections from ResumeParserAgent."""

    model_config = ConfigDict(frozen=True)

    sections: list[ResumeSectionFields] = Field(
        description="Ordered sections from top to bottom",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        secs = find_value(
            data,
            "sections",
            "resume_sections",
            "resumeSections",
            "parsed_sections",
        )
        if isinstance(secs, list):
            return {"sections": secs}
        return {"sections": _dict_to_sections(data)}
