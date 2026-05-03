"""Helpers to normalise variable LLM JSON into canonical field names."""

from __future__ import annotations

import re
from typing import Any

from alignai.domain.models import MatchLabel


def _norm_key(key: str) -> str:
    """Normalise a dict key: camelCase → snake_case, lowercase, collapse separators."""
    key = re.sub(r"([a-z])([A-Z])", r"\1_\2", key)
    return re.sub(r"[\s\-]+", "_", key.strip()).lower()


def find_value(data: dict[str, Any], *keys: str) -> Any | None:
    """Case-insensitive, camelCase-aware lookup across multiple alias keys."""
    lowered = {_norm_key(k): v for k, v in data.items()}
    for key in keys:
        hit = lowered.get(_norm_key(key))
        if hit is not None:
            return hit
    return None


def coerce_str(value: Any) -> str:
    """Flatten a value to plain text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(coerce_str(item) for item in value)
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            parts.append(f"{k}: {coerce_str(v)}")
        return "\n".join(parts)
    return str(value)


def coerce_int(value: Any, low: int, high: int) -> int:
    """Coerce to bounded int."""
    if isinstance(value, dict):
        for k in ("score", "value", "rating", "result"):
            if k in value:
                return coerce_int(value[k], low, high)
        for k, v in value.items():
            if _norm_key(k) in ("score", "value", "rating"):
                return coerce_int(v, low, high)
    if isinstance(value, str):
        m = re.search(r"\d+", value)
        if m:
            return max(low, min(high, int(m.group())))
    if isinstance(value, float):
        return max(low, min(high, int(value)))
    if isinstance(value, int):
        return max(low, min(high, value))
    return low


def coerce_str_list(value: Any) -> list[str]:
    """Coerce to a list of strings."""
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str):
        items = re.split(r"[,;\n]+", value)
        return [re.sub(r"^\s*\d+[.)]\s*", "", it).strip("- ").strip() for it in items if it.strip()]
    if isinstance(value, dict):
        for v in value.values():
            if isinstance(v, list):
                return coerce_str_list(v)
    return [str(value)] if value else []


_MATCH_LABEL_MAP: dict[str, MatchLabel] = {}
for _member in MatchLabel:
    _lv = _member.value.lower()
    _MATCH_LABEL_MAP[_lv] = _member
    _MATCH_LABEL_MAP[_lv.replace(" ", "")] = _member
    _MATCH_LABEL_MAP[_lv.replace(" ", "_")] = _member
    _first = _lv.split()[0]
    _MATCH_LABEL_MAP[_first] = _member


def coerce_match_label(value: Any, fallback_score: int = 3) -> MatchLabel:
    """Case-insensitive MatchLabel matching with score-based fallback."""
    if isinstance(value, MatchLabel):
        return value
    if isinstance(value, str):
        normalized = re.sub(r"[\s_\-]+", " ", value.strip().lower())
        hit = _MATCH_LABEL_MAP.get(normalized)
        if hit:
            return hit
        hit = _MATCH_LABEL_MAP.get(normalized.replace(" ", ""))
        if hit:
            return hit
        for k, v in _MATCH_LABEL_MAP.items():
            if normalized.startswith(k.split()[0] if " " in k else k):
                return v
    score_map: dict[int, MatchLabel] = {
        5: MatchLabel.STRONG_MATCH,
        4: MatchLabel.GOOD_MATCH,
        3: MatchLabel.FAIR_MATCH,
        2: MatchLabel.LOW_MATCH,
        1: MatchLabel.WEAK_MATCH,
    }
    return score_map.get(fallback_score, MatchLabel.FAIR_MATCH)
