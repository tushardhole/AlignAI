"""Tests for MergedResumeFields LLM shape coercion."""

from __future__ import annotations

from alignai.agents.merged_resume_fields import MergedResumeFields


def test_merged_resume_coerces_semantic_resume_dict_to_content() -> None:
    raw = {
        "contact": {"name": "TEST USER"},
        "summary": "Engineer summary.",
        "experience": [
            {
                "jobTitle": "AI Engineer",
                "company": "PMG",
                "jobSummary": "Built features.",
                "requirements": ["3+ years dev"],
                "responsibilities": ["Shipped code."],
            }
        ],
        "skills": ["Python", "Go"],
    }
    out = MergedResumeFields.model_validate(raw)
    assert "TEST USER" in out.content
    assert "Engineer summary" in out.content
    assert "PMG" in out.content
    assert "Python" in out.content


def test_merged_resume_preserves_content_key() -> None:
    out = MergedResumeFields.model_validate({"content": "  One string  "})
    assert out.content == "One string"
