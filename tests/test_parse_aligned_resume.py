"""Tests for resume parsing from LLM output."""

import pytest

from alignai.application.parse_aligned_resume import parse_resume_text


def test_parse_resume_text() -> None:
    """Test parsing resume from JSON format."""
    json_input = """{
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "location": "San Francisco, CA",
        "summary": "Experienced software engineer",
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Tech Corp",
                "dates": "2020-2023",
                "bullets": ["Led team", "Improved performance"]
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "school": "MIT",
                "graduation_date": "2020"
            }
        ],
        "skills": ["Python", "JavaScript", "React"]
    }"""
    result = parse_resume_text(json_input)
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert len(result["experience"]) == 1
    assert result["experience"][0]["title"] == "Senior Engineer"


def test_parse_resume_text_plain_text() -> None:
    """Test parsing resume from plain text format."""
    text_input = """John Doe
john@example.com
555-123-4567

Professional Summary
Experienced software engineer with 5+ years of experience.

Professional Experience
Senior Engineer

Education
BS Computer Science

Skills
Python, JavaScript, React"""

    result = parse_resume_text(text_input)
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["phone"] == "555-123-4567"
    assert isinstance(result["experience"], list)
    assert isinstance(result["education"], list)
    assert len(result["skills"]) > 0


def test_parse_resume_text_empty_input() -> None:
    """Test parsing empty resume."""
    result = parse_resume_text("")
    assert result["name"] == ""
    assert isinstance(result["experience"], list)
    assert isinstance(result["education"], list)
    assert isinstance(result["skills"], list)


def test_parse_resume_text_validation() -> None:
    """Test that parsed resume has valid structure."""
    text_input = "John Doe\njohn@example.com\n\nProfessional Experience\nEngineer"
    result = parse_resume_text(text_input)

    # Check all required keys exist
    assert "name" in result
    assert "email" in result
    assert "phone" in result
    assert "location" in result
    assert "summary" in result
    assert "experience" in result
    assert "education" in result
    assert "skills" in result

    # Check types
    assert isinstance(result["experience"], list)
    assert isinstance(result["education"], list)
    assert isinstance(result["skills"], list)
