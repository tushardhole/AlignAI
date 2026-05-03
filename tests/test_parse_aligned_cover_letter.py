"""Tests for cover letter parsing from LLM output."""

import pytest

from alignai.application.parse_aligned_cover_letter import parse_cover_letter_text


def test_parse_cover_letter_text() -> None:
    """Test parsing cover letter from JSON format."""
    json_input = """{
        "candidate_name": "John Doe",
        "date": "January 15, 2024",
        "paragraphs": [
            "I am writing to express my interest in the Software Engineer position.",
            "With 5 years of experience in full-stack development, I am confident.",
            "I look forward to discussing this opportunity with you."
        ]
    }"""
    result = parse_cover_letter_text(json_input)
    assert result["candidate_name"] == "John Doe"
    assert result["date"] == "January 15, 2024"
    assert len(result["paragraphs"]) == 3


def test_parse_cover_letter_text_plain_text() -> None:
    """Test parsing cover letter from plain text format."""
    text_input = """Dear Hiring Manager,

I am writing to express my strong interest in the Software Engineer position at TechCorp.
With 5+ years of experience in full-stack development, I am confident in my ability to contribute.

I have successfully led teams, improved system performance, and delivered complex projects on time.
My expertise in Python, JavaScript, and cloud technologies aligns well with your requirements.

I look forward to discussing how my skills and experience can contribute to your team.

Regards,
John Doe"""

    result = parse_cover_letter_text(text_input)
    assert result["candidate_name"] == "John Doe"
    assert isinstance(result["paragraphs"], list)
    assert len(result["paragraphs"]) > 0


def test_parse_cover_letter_text_empty_input() -> None:
    """Test parsing empty cover letter."""
    result = parse_cover_letter_text("")
    assert result["candidate_name"] == "Candidate"
    assert isinstance(result["paragraphs"], list)
    assert "date" in result


def test_parse_cover_letter_text_validation() -> None:
    """Test that parsed cover letter has valid structure."""
    text_input = "I am interested in this position.\n\nRegards,\nJane Smith"
    result = parse_cover_letter_text(text_input)

    # Check all required keys exist
    assert "candidate_name" in result
    assert "date" in result
    assert "paragraphs" in result

    # Check types
    assert isinstance(result["paragraphs"], list)
    assert isinstance(result["date"], str)


def test_parse_cover_letter_text_name_extraction() -> None:
    """Test extraction of candidate name from signature."""
    text_input = """Dear Hiring Manager,

I am interested in the position.

Regards,
Jane Smith"""
    result = parse_cover_letter_text(text_input)
    assert result["candidate_name"] == "Jane Smith"
