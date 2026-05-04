"""Parse aligned resume text into structured data for templating."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_resume_text(resume_text: str) -> dict[str, Any]:
    """Parse resume text into structured data for professional templating.

    Supports hybrid parsing: tries JSON first, falls back to text-based parsing.

    Args:
        resume_text: Aligned resume text from LLM (plain text or JSON)

    Returns:
        Dict with keys: name, email, phone, location, summary, experience, education, skills
    """
    # Try JSON parsing first
    try:
        data = json.loads(resume_text)
        if isinstance(data, dict):
            return _validate_resume_structure(data)
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: text-based parsing
    return _parse_resume_text(resume_text)


def _parse_resume_text(text: str) -> dict[str, Any]:
    """Parse plain text resume into structured data using heuristics."""
    data: dict[str, Any] = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
    }

    lines = text.strip().split("\n")

    # Extract email and phone from first few lines
    for line in lines[:10]:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", line)
        if email_match:
            data["email"] = email_match.group()

        phone_match = re.search(r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", line)
        if phone_match:
            data["phone"] = phone_match.group()

    # Extract name (typically first non-empty line)
    for line in lines:
        line = line.strip()
        if line and not any(c in line for c in ["@", "http", "|"]):
            data["name"] = line
            break

    # Extract sections based on headers
    current_section = None
    current_entry: dict[str, Any] = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers
        upper_line = line.upper()
        if any(header in upper_line for header in ["PROFESSIONAL SUMMARY", "SUMMARY"]):
            current_section = "summary"
            current_entry = {}
            continue
        elif "EXPERIENCE" in upper_line or "PROFESSIONAL EXPERIENCE" in upper_line:
            current_section = "experience"
            current_entry = {}
            continue
        elif "EDUCATION" in upper_line:
            current_section = "education"
            current_entry = {}
            continue
        elif "SKILLS" in upper_line:
            current_section = "skills"
            continue

        # Process line based on current section
        if current_section == "summary":
            if data["summary"]:
                data["summary"] += " " + line
            else:
                data["summary"] = line

        elif current_section == "experience":
            if line.startswith("•") or line.startswith("-"):
                # Bullet point
                bullet = line.lstrip("•- ").strip()
                if current_entry and "bullets" in current_entry:
                    current_entry["bullets"].append(bullet)
            else:
                # New entry header
                if current_entry and "title" in current_entry:
                    data["experience"].append(current_entry)
                current_entry = {"title": line, "bullets": []}

        elif current_section == "education":
            if line and not line.startswith("•"):
                if current_entry and "degree" in current_entry:
                    data["education"].append(current_entry)
                current_entry = {"degree": line}

        elif current_section == "skills":
            skills = [s.strip() for s in line.split(",")]
            data["skills"].extend(skills)

    # Add last entry
    if current_section == "experience" and current_entry:
        data["experience"].append(current_entry)
    elif current_section == "education" and current_entry:
        data["education"].append(current_entry)

    return _validate_resume_structure(data)


def _validate_resume_structure(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize resume data structure."""
    # Ensure all required keys exist
    required_keys = [
        "name",
        "email",
        "phone",
        "location",
        "summary",
        "experience",
        "education",
        "skills",
    ]
    for key in required_keys:
        if key not in data:
            data[key] = "" if key in ["name", "email", "phone", "location", "summary"] else []

    # Clean up empty strings
    for key in ["name", "email", "phone", "location", "summary"]:
        if not data[key]:
            data[key] = ""

    # Ensure lists are lists
    for key in ["experience", "education", "skills"]:
        if not isinstance(data[key], list):
            data[key] = []

    # Validate experience entries
    validated_experience = []
    for exp in data["experience"]:
        if isinstance(exp, dict):
            validated_experience.append(
                {
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "dates": exp.get("dates", ""),
                    "bullets": exp.get("bullets", [])
                    if isinstance(exp.get("bullets"), list)
                    else [],
                }
            )
    data["experience"] = validated_experience

    # Validate education entries
    validated_education = []
    for edu in data["education"]:
        if isinstance(edu, dict):
            validated_education.append(
                {
                    "degree": edu.get("degree", ""),
                    "school": edu.get("school", ""),
                    "graduation_date": edu.get("graduation_date", ""),
                }
            )
    data["education"] = validated_education

    # Ensure skills is a list of strings
    data["skills"] = [str(s) for s in data["skills"] if s]

    return data
