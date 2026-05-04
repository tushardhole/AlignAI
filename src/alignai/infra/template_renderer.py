"""Jinja2-based template rendering for resumes and cover letters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class TemplateRenderer:
    """Renders professional resume and cover letter HTML using Jinja2 templates."""

    def __init__(self) -> None:
        """Initialize template renderer with templates directory."""
        templates_dir = Path(__file__).parent / "templates"
        if not templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_resume(self: TemplateRenderer, resume_data: dict[str, Any]) -> str:
        """Render professional resume HTML from structured data.

        Args:
            resume_data: Dict with keys: name, email, phone, location, summary,
                        experience (list), education (list), skills (list)

        Returns:
            Complete HTML string ready for PDF rendering.

        Raises:
            TemplateNotFound: If resume template not found.
            KeyError: If required fields missing from resume_data.
        """
        try:
            template = self._env.get_template("resume.html")
        except TemplateNotFound as e:
            raise TemplateNotFound(f"resume.html template not found: {e}") from e

        # Ensure required fields
        if "name" not in resume_data:
            resume_data["name"] = "Resume"

        return template.render(**resume_data)

    def render_cover_letter(self: TemplateRenderer, cover_letter_data: dict[str, Any]) -> str:
        """Render professional cover letter HTML from structured data.

        Args:
            cover_letter_data: Dict with keys: candidate_name, date, paragraphs (list)

        Returns:
            Complete HTML string ready for PDF rendering.

        Raises:
            TemplateNotFound: If cover letter template not found.
            KeyError: If required fields missing from cover_letter_data.
        """
        try:
            template = self._env.get_template("cover_letter.html")
        except TemplateNotFound as e:
            raise TemplateNotFound(f"cover_letter.html template not found: {e}") from e

        # Ensure required fields
        if "candidate_name" not in cover_letter_data:
            cover_letter_data["candidate_name"] = "Candidate"
        if "paragraphs" not in cover_letter_data:
            cover_letter_data["paragraphs"] = []
        if "date" not in cover_letter_data:
            from datetime import date

            cover_letter_data["date"] = date.today().strftime("%B %d, %Y")

        return template.render(**cover_letter_data)
