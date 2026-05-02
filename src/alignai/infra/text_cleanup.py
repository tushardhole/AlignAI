"""Deterministic cleanup for LLM-generated text before persistence or PDF render."""

from __future__ import annotations

import re


def clean(text: str) -> str:
    """Normalize punctuation and whitespace from model output.

    - Em-dash / horizontal bar between words to single ASCII space
    - En-dash between non-digits to single space (preserves numeric ranges like 2019-2024)
    - Runs of double underscores to single space
    - Collapse repeated whitespace
    """
    if not text:
        return text
    # Em dash U+2014, horizontal bar U+2015 (with surrounding whitespace)
    out = re.sub(r"\s*[\u2014\u2015]\s*", " ", text)
    # En dash U+2013 only when not part of a digit range
    out = re.sub(r"(?<!\d)\s*\u2013\s*(?!\d)", " ", out)
    out = re.sub(r"_{2,}", " ", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()
