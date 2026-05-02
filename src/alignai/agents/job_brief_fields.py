"""Structured LLM output for the job analyst agent."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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
