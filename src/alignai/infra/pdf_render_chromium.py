"""Render HTML to PDF using Playwright Chromium."""

from __future__ import annotations

from pathlib import Path

from playwright.async_api import async_playwright


class ChromiumPdfRenderer:
    """Print HTML to PDF via headless Chromium (bundled with Playwright)."""

    def __init__(self) -> None:
        self._playwright_cm = None

    async def render(self, html: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.set_content(html, wait_until="networkidle")
                await page.pdf(path=str(output_path), format="Letter", print_background=True)
            finally:
                await browser.close()
        return output_path
