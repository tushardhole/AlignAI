"""Tests for SectionAlignedFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.section_aligned_fields import SectionAlignedFields


def test_section_aligned_coerces_certifications_list_shape() -> None:
    raw = {"Certifications": [{"name": "AWS Certified Cloud Practitioner"}]}
    out = SectionAlignedFields.model_validate(raw)
    assert "AWS Certified Cloud Practitioner" in out.aligned_content
    assert out.aligned_content.strip().startswith("-")


def test_section_aligned_preserves_aligned_content() -> None:
    out = SectionAlignedFields.model_validate({"aligned_content": "  Hello  "})
    assert out.aligned_content == "Hello"


def test_section_aligned_coerces_plain_heading_string_value() -> None:
    out = SectionAlignedFields.model_validate({"Summary": "Backend engineer."})
    assert out.aligned_content == "Backend engineer."
