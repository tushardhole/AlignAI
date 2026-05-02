"""HTML wrappers for PDF rendering (no external deps)."""

from __future__ import annotations

from html import escape


def format_resume_pdf_html(title: str, body_plain: str) -> str:
    """Build minimal print-friendly HTML for an aligned resume."""
    safe_title = escape(title)
    safe_body = escape(body_plain)
    return (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="utf-8"/><style>'
        "body{font-family:Georgia,serif;margin:1in;font-size:11pt;line-height:1.35;}"
        "pre{white-space:pre-wrap;font-family:inherit;margin:0}"
        "</style></head><body>"
        f"<h1>{safe_title}</h1><pre>{safe_body}</pre>"
        "</body></html>"
    )


def format_cover_letter_pdf_html(title: str, body_plain: str) -> str:
    """Build minimal print-friendly HTML for a cover letter."""
    safe_title = escape(title)
    safe_body = escape(body_plain)
    return (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="utf-8"/><style>'
        "body{font-family:Georgia,serif;margin:1in;font-size:11pt;line-height:1.45;}"
        "pre{white-space:pre-wrap;font-family:inherit;margin:0}"
        "</style></head><body>"
        f"<h1>{safe_title}</h1><pre>{safe_body}</pre>"
        "</body></html>"
    )
