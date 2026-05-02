"""Tests for HTML helpers used before Chromium PDF render."""

from __future__ import annotations

from alignai.application.pdf_markup import format_cover_letter_pdf_html, format_resume_pdf_html


def test_printable_resume_html_format_resume_pdf_html() -> None:
    html = format_resume_pdf_html("Role & <Title>", "Line1\nLine2")
    assert "Role &amp; &lt;Title&gt;" in html
    assert "Line1" in html
    assert "<!DOCTYPE html>" in html


def test_printable_cover_html_format_cover_letter_pdf_html() -> None:
    html = format_cover_letter_pdf_html("Hello", "Body <text>")
    assert "Body &lt;text&gt;" in html
    assert "Hello" in html
