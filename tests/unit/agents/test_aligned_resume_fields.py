"""Tests for AlignedResumeFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.aligned_resume_fields import AlignedResumeFields


def test_resume_coerces_resume_key() -> None:
    out = AlignedResumeFields.model_validate({"resume": "Experience\nAcme"})
    assert out.content == "Experience\nAcme"


def test_resume_single_unknown_string_key() -> None:
    out = AlignedResumeFields.model_validate({"alignedResumeText": "Full text here"})
    assert out.content == "Full text here"
