"""Parse aligned cover letter text into structured data for templating."""

from __future__ import annotations

import json
from datetime import date
from typing import Any


def parse_cover_letter_text(cover_letter_text: str) -> dict[str, Any]:
    """Parse cover letter text into structured data for professional templating.

    Supports hybrid parsing: tries JSON first, falls back to text-based parsing.

    Args:
        cover_letter_text: Aligned cover letter text from LLM (plain text or JSON)

    Returns:
        Dict with keys: candidate_name, date, paragraphs
    """
    # Try JSON parsing first
    try:
        data = json.loads(cover_letter_text)
        if isinstance(data, dict):
            return _validate_cover_letter_structure(data)
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: text-based parsing
    return _parse_cover_letter_text(cover_letter_text)


def _parse_cover_letter_text(text: str) -> dict[str, Any]:
    """Parse plain text cover letter into structured data."""
    data: dict[str, Any] = {
        "candidate_name": "",
        "date": date.today().strftime("%B %d, %Y"),
        "paragraphs": [],
    }

    lines = text.strip().split("\n")

    # Extract candidate name from last line or signature section
    for line in reversed(lines[-5:]):
        line = line.strip()
        if (
            line
            and not any(c in line for c in ["@", "http", "Regards", "Dear"])
            and len(line.split()) <= 3
        ):  # Likely a name (2-3 words max)
            data["candidate_name"] = line
            break

    # Extract paragraphs: split on blank lines
    current_paragraph = ""
    for line in lines:
        line = line.strip()

        # Skip greeting and closing lines
        if any(
            skip in line for skip in ["Dear", "Regards", "Sincerely", "Best regards", "Thank you"]
        ):
            if current_paragraph:
                data["paragraphs"].append(current_paragraph.strip())
                current_paragraph = ""
            continue

        # Build paragraphs from text
        if line:
            current_paragraph += " " + line if current_paragraph else line
        elif current_paragraph:
            data["paragraphs"].append(current_paragraph.strip())
            current_paragraph = ""

    # Add last paragraph
    if current_paragraph:
        data["paragraphs"].append(current_paragraph.strip())

    # Remove empty paragraphs
    data["paragraphs"] = [p for p in data["paragraphs"] if p and len(p) > 10]

    return _validate_cover_letter_structure(data)


def _validate_cover_letter_structure(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize cover letter data structure."""
    # Ensure required keys exist
    if "candidate_name" not in data:
        data["candidate_name"] = ""
    if "date" not in data:
        data["date"] = date.today().strftime("%B %d, %Y")
    if "paragraphs" not in data:
        data["paragraphs"] = []

    # Clean up candidate name
    if not data["candidate_name"]:
        data["candidate_name"] = "Candidate"

    # Ensure paragraphs is a list of strings
    if not isinstance(data["paragraphs"], list):
        data["paragraphs"] = []
    data["paragraphs"] = [str(p) for p in data["paragraphs"] if p]

    return data
