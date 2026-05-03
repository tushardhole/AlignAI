"""Structured LLM output for the job analyst agent."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, coerce_str_list, find_value

_SKIP_VALUES = {"none", "n/a", "unknown", "not specified", "tbd", "n/a."}


def _is_valid_skill(s: str) -> bool:
    return bool(s) and s.lower().strip() not in _SKIP_VALUES


def _experience_to_skills(exp: Any) -> list[str]:
    """Convert {domain: years} dict to readable strings like '3 years in software development'."""
    if not isinstance(exp, dict):
        return []
    result = []
    for key, val in exp.items():
        label = str(key).replace("_", " ")
        if isinstance(val, (int, float)) and val:
            result.append(f"{int(val)} years in {label}")
        elif isinstance(val, str) and val and val.lower() not in _SKIP_VALUES:
            result.append(f"{val} in {label}")
    return result


def _collect_must_have_skills(data: dict[str, Any]) -> list[str]:
    # Canonical key present → use it directly
    canonical = find_value(data, "must_have_skills", "must_have", "hard_requirements")
    if canonical is not None:
        return [s for s in coerce_str_list(canonical) if _is_valid_skill(s)]

    skills: list[str] = []
    # Explicit skills field (list or dict with 'required' subkey)
    raw = find_value(data, "skills", "technical_skills")
    if isinstance(raw, list):
        skills.extend(coerce_str_list(raw))
    elif isinstance(raw, dict):
        req = find_value(raw, "required", "must_have", "hard_requirements")
        if req:
            skills.extend(coerce_str_list(req))

    # Individual skill-source fields (order matters: more specific first)
    for key in (
        "languages",
        "required_languages",
        "frameworks",
        "required_frameworks",
        "requirements",
        "required_skills",
        "key_skills",
        "essential_skills",
    ):
        val = find_value(data, key)
        if val:
            skills.extend(coerce_str_list(val))

    # Experience dict → readable strings
    exp = find_value(data, "required_experience", "experience_requirements")
    skills.extend(_experience_to_skills(exp))

    # Certifications and responsibilities as supporting context
    for key in ("certifications", "required_certifications"):
        val = find_value(data, key)
        if val:
            skills.extend(coerce_str_list(val))
    resp = find_value(data, "responsibilities", "key_responsibilities")
    if resp:
        skills.extend(coerce_str_list(resp)[:3])

    return list(dict.fromkeys(s for s in skills if _is_valid_skill(s)))


def _collect_nice_to_have_skills(data: dict[str, Any]) -> list[str]:
    hit = find_value(
        data,
        "nice_to_have_skills",
        "desired_skills",
        "preferred_skills",
        "optional_skills",
        "bonus_skills",
        "nice_to_have",
    )
    if hit:
        return [s for s in coerce_str_list(hit) if _is_valid_skill(s)]
    raw = find_value(data, "skills")
    if isinstance(raw, dict):
        nice = find_value(raw, "nice_to_have", "nice_to_have_skills", "preferred", "optional")
        if nice:
            return [s for s in coerce_str_list(nice) if _is_valid_skill(s)]
    return []


def _build_summary(data: dict[str, Any]) -> str:
    hit = find_value(data, "summary", "description", "overview", "job_summary", "about")
    if hit:
        return coerce_str(hit)
    parts: list[str] = []
    for key in ("company", "company_name", "employer"):
        val = find_value(data, key)
        if isinstance(val, str) and val:
            parts.append(val)
            break
    for key in ("location", "job_location"):
        val = find_value(data, key)
        if isinstance(val, str) and val:
            parts.append(val)
            break
    for key in ("company_description", "job_description", "about_company"):
        val = find_value(data, key)
        if isinstance(val, str) and val:
            parts.append(val)
            break
    for key in ("experience", "years_of_experience"):
        val = find_value(data, key)
        if isinstance(val, str) and val:
            parts.append(val)
            break
    return " — ".join(parts)


class JobBriefFields(BaseModel):
    """Extracted job summary for downstream alignment agents."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(description="Canonical job title")
    summary: str = Field(description="2-4 sentence summary of the role")
    must_have_skills: list[str] = Field(
        default_factory=list,
        description="Hard requirements explicitly stated in the posting",
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list,
        description="Preferred but optional qualifications",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        title = find_value(data, "title", "job_title", "position", "role", "position_title")
        result: dict[str, Any] = {
            "title": coerce_str(title).strip() if title else "Untitled",
            "summary": _build_summary(data),
            "must_have_skills": _collect_must_have_skills(data),
            "nice_to_have_skills": _collect_nice_to_have_skills(data),
        }
        return result
