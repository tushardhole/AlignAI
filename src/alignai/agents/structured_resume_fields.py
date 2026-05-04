"""Pydantic model for LLM-structured resume JSON output."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from alignai.agents.llm_json_coercion import coerce_str, coerce_str_list, find_value


class StructuredResumeFields(BaseModel):
    """Resume structured into template-ready JSON by the structuring agent."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="")
    email: str = Field(default="")
    phone: str = Field(default="")
    location: str = Field(default="")
    summary: str = Field(default="")
    links: list[dict[str, str]] = Field(default_factory=list)
    skills_by_category: dict[str, list[str]] = Field(default_factory=dict)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, str]] = Field(default_factory=list)
    certifications: list[dict[str, str]] = Field(default_factory=list)
    projects: list[dict[str, str]] = Field(default_factory=list)
    projects_title: str = Field(default="")
    volunteer: list[dict[str, Any]] = Field(default_factory=list)
    affiliations: list[str] = Field(default_factory=list)
    awards: list[dict[str, str]] = Field(default_factory=list)
    publications: list[dict[str, str]] = Field(default_factory=list)
    extra_sections: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        return _normalize_resume_dict(data)


def _normalize_resume_dict(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize LLM output dict into canonical resume schema."""
    out: dict[str, Any] = {}

    out["name"] = _str_field(raw, "name", "candidate_name", "candidateName", "full_name")
    out["email"] = _str_field(raw, "email", "e_mail", "emailAddress")
    out["phone"] = _str_field(raw, "phone", "telephone", "phone_number", "phoneNumber")
    out["location"] = _str_field(raw, "location", "city", "address", "city_state")
    out["summary"] = _str_field(
        raw,
        "summary",
        "professional_summary",
        "professionalSummary",
        "profile",
        "objective",
        "about",
    )

    out["links"] = _normalize_links(raw)
    out["skills_by_category"] = _normalize_skills(raw)
    out["experience"] = _normalize_experience(raw)
    out["education"] = _normalize_education(raw)
    out["certifications"] = _normalize_simple_list(
        raw,
        ["certifications", "licenses", "credentials"],
        keys=("name", "issuer", "date"),
    )
    out["projects"] = _normalize_projects(raw)
    out["projects_title"] = _str_field(raw, "projects_title", "projectsTitle")
    out["volunteer"] = _normalize_volunteer(raw)
    out["affiliations"] = _normalize_affiliations(raw)
    out["awards"] = _normalize_simple_list(
        raw,
        ["awards", "honors", "recognition"],
        keys=("title", "description", "issuer", "date"),
    )
    out["publications"] = _normalize_simple_list(
        raw,
        ["publications", "papers", "research"],
        keys=("title", "venue", "date", "description"),
    )
    out["extra_sections"] = _normalize_extra_sections(raw)
    out["extra_sections"] += _collect_unrecognized_sections(raw)

    return out


def _str_field(data: dict[str, Any], *keys: str) -> str:
    hit = find_value(data, *keys)
    if hit is None:
        return ""
    return coerce_str(hit).strip()


def _normalize_links(raw: dict[str, Any]) -> list[dict[str, str]]:
    hit = find_value(raw, "links", "urls", "profiles", "websites")
    if not isinstance(hit, list):
        return []
    result: list[dict[str, str]] = []
    for item in hit:
        if isinstance(item, dict):
            url = find_value(item, "url", "href", "link") or ""
            display = find_value(item, "display", "text", "label") or url
            result.append(
                {
                    "url": _ensure_url_protocol(coerce_str(url)),
                    "display": coerce_str(display),
                }
            )
        elif isinstance(item, str):
            result.append({"url": _ensure_url_protocol(item), "display": item})
    return result


def _ensure_url_protocol(url: str) -> str:
    """Ensure URL has https:// prefix for proper linking."""
    url = url.strip()
    if not url:
        return url
    if url.startswith(("http://", "https://", "mailto:")):
        return url
    return "https://" + url


def _normalize_skills(raw: dict[str, Any]) -> dict[str, list[str]]:
    hit = find_value(
        raw,
        "skills_by_category",
        "skillsByCategory",
        "skills",
        "technical_skills",
        "technicalSkills",
        "core_competencies",
        "coreCompetencies",
    )
    if isinstance(hit, dict):
        result: dict[str, list[str]] = {}
        for k, v in hit.items():
            result[str(k)] = coerce_str_list(v)
        return result
    if isinstance(hit, list):
        flat = coerce_str_list(hit)
        if flat:
            return {"Skills": flat}
    return {}


def _normalize_experience(raw: dict[str, Any]) -> list[dict[str, Any]]:
    hit = find_value(
        raw,
        "experience",
        "work_experience",
        "workExperience",
        "professional_experience",
        "professionalExperience",
        "employment",
        "employment_history",
    )
    if not isinstance(hit, list):
        return []
    result: list[dict[str, Any]] = []
    for item in hit:
        if not isinstance(item, dict):
            continue
        entry: dict[str, Any] = {
            "title": _str_field(item, "title", "role", "position", "job_title"),
            "company": _str_field(item, "company", "employer", "organization", "org"),
            "dates": _str_field(item, "dates", "duration", "period", "date_range", "dateRange"),
            "bullets": coerce_str_list(
                find_value(item, "bullets", "responsibilities", "achievements", "details") or []
            ),
            "meta": _normalize_meta(item),
        }
        result.append(entry)
    return result


def _normalize_meta(item: dict[str, Any]) -> list[dict[str, str]]:
    hit = find_value(item, "meta", "metadata", "tags")
    if isinstance(hit, list):
        return [
            {"label": coerce_str(m.get("label", "")), "value": coerce_str(m.get("value", ""))}
            for m in hit
            if isinstance(m, dict)
        ]
    meta: list[dict[str, str]] = []
    for key in (
        "tech",
        "technologies",
        "tools",
        "stack",
        "specialties",
        "platforms",
        "environment",
        "software",
        "products",
    ):
        val = find_value(item, key)
        if val:
            label = key.capitalize()
            meta.append({"label": label, "value": coerce_str(val)})
    return meta


def _normalize_education(raw: dict[str, Any]) -> list[dict[str, str]]:
    hit = find_value(raw, "education", "academic_background", "academicBackground")
    if not isinstance(hit, list):
        return []
    result: list[dict[str, str]] = []
    for item in hit:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "degree": _str_field(item, "degree", "qualification", "program"),
                "school": _str_field(item, "school", "institution", "university", "college"),
                "location": _str_field(
                    item,
                    "location",
                    "city",
                    "address",
                    "city_state",
                    "state",
                ),
                "graduation_date": _str_field(
                    item,
                    "graduation_date",
                    "graduationDate",
                    "date",
                    "year",
                ),
            }
        )
    return result


def _normalize_projects(raw: dict[str, Any]) -> list[dict[str, str]]:
    hit = find_value(
        raw,
        "projects",
        "side_projects",
        "sideProjects",
        "personal_projects",
        "personalProjects",
    )
    if not isinstance(hit, list):
        return []
    result: list[dict[str, str]] = []
    for item in hit:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "name": _str_field(item, "name", "title", "project_name"),
                "link": _str_field(item, "link", "url", "github", "repo"),
                "url": _str_field(item, "url", "link", "href"),
                "description": _str_field(item, "description", "desc", "summary"),
            }
        )
    return result


def _normalize_volunteer(raw: dict[str, Any]) -> list[dict[str, Any]]:
    hit = find_value(
        raw,
        "volunteer",
        "volunteer_experience",
        "volunteerExperience",
        "community_involvement",
    )
    if not isinstance(hit, list):
        return []
    result: list[dict[str, Any]] = []
    for item in hit:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "title": _str_field(item, "title", "role", "position"),
                "company": _str_field(item, "company", "organization", "org"),
                "dates": _str_field(item, "dates", "duration", "period"),
                "bullets": coerce_str_list(
                    find_value(item, "bullets", "responsibilities", "details") or []
                ),
            }
        )
    return result


def _normalize_affiliations(raw: dict[str, Any]) -> list[str]:
    hit = find_value(
        raw,
        "affiliations",
        "professional_affiliations",
        "professionalAffiliations",
        "memberships",
    )
    return coerce_str_list(hit) if hit else []


def _normalize_simple_list(
    raw: dict[str, Any],
    aliases: list[str],
    keys: tuple[str, ...],
) -> list[dict[str, str]]:
    hit = find_value(raw, *aliases)
    if not isinstance(hit, list):
        return []
    result: list[dict[str, str]] = []
    for item in hit:
        if isinstance(item, dict):
            entry = {k: _str_field(item, k) for k in keys}
            result.append(entry)
        elif isinstance(item, str) and keys:
            result.append({keys[0]: item, **dict.fromkeys(keys[1:], "")})
    return result


def _normalize_extra_sections(raw: dict[str, Any]) -> list[dict[str, Any]]:
    hit = find_value(raw, "extra_sections", "extraSections", "additional_sections")
    if not isinstance(hit, list):
        return []
    result: list[dict[str, Any]] = []
    _title_keys = (
        "title",
        "heading",
        "name",
        "section",
        "section_name",
        "sectionName",
        "header",
        "label",
    )
    _lines_keys = ("lines", "content", "items", "entries", "bullets")
    for item in hit:
        if isinstance(item, dict):
            title = _str_field(item, *_title_keys)
            lines = coerce_str_list(find_value(item, *_lines_keys) or [])
            if not title and not lines:
                title, lines = _infer_title_from_dict(item, _title_keys, _lines_keys)
            result.append({"title": title, "lines": lines})
    return result


def _infer_title_from_dict(
    item: dict[str, Any],
    title_keys: tuple[str, ...],
    lines_keys: tuple[str, ...],
) -> tuple[str, list[str]]:
    """Handle LLM format where the key IS the title and the value is the lines."""
    skip = {k.lower() for k in title_keys + lines_keys}
    for k, v in item.items():
        if k.lower() in skip:
            continue
        if isinstance(v, list):
            return _key_to_title(k), coerce_str_list(v)
    return "", []


_KNOWN_KEYS = frozenset(
    {
        "name",
        "candidate_name",
        "candidatename",
        "full_name",
        "fullname",
        "email",
        "e_mail",
        "emailaddress",
        "phone",
        "telephone",
        "phone_number",
        "phonenumber",
        "location",
        "city",
        "address",
        "city_state",
        "citystate",
        "summary",
        "professional_summary",
        "professionalsummary",
        "profile",
        "objective",
        "about",
        "links",
        "urls",
        "profiles",
        "websites",
        "skills_by_category",
        "skillsbycategory",
        "skills",
        "technical_skills",
        "technicalskills",
        "core_competencies",
        "corecompetencies",
        "experience",
        "work_experience",
        "workexperience",
        "professional_experience",
        "professionalexperience",
        "employment",
        "employment_history",
        "education",
        "academic_background",
        "academicbackground",
        "certifications",
        "licenses",
        "credentials",
        "projects",
        "projects_title",
        "projectstitle",
        "volunteer",
        "volunteer_experience",
        "volunteerexperience",
        "affiliations",
        "professional_affiliations",
        "professionalaffiliations",
        "awards",
        "honors",
        "recognition",
        "publications",
        "papers",
        "research",
        "extra_sections",
        "extrasections",
        "additional_sections",
    }
)


def _collect_unrecognized_sections(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect LLM keys not matching known fields and treat them as extra sections."""
    result: list[dict[str, Any]] = []
    for key, val in raw.items():
        norm_key = key.lower().replace(" ", "").replace("-", "").replace("_", "")
        if norm_key in {k.replace("_", "") for k in _KNOWN_KEYS}:
            continue
        if isinstance(val, list) and val:
            lines = coerce_str_list(val)
            if lines:
                title = _key_to_title(key)
                result.append({"title": title, "lines": lines})
    return result


def _key_to_title(key: str) -> str:
    """Convert a key like 'open_source_contributions' or 'PersonalAIProjects' to title."""
    import re

    if "_" in key or "-" in key:
        words = key.replace("_", " ").replace("-", " ").split()
        return " ".join(w[0].upper() + w[1:] for w in words)
    if " " in key:
        return " ".join(w[0].upper() + w[1:] for w in key.split())
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", key)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return " ".join(w[0].upper() + w[1:] for w in spaced.split())
