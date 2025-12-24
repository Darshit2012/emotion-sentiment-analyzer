"""Lightweight explainability helpers for highlighting important tokens."""
from __future__ import annotations

import re
from typing import Iterable, List, Tuple


TokenScores = Iterable[Tuple[str, float]]


def _color_from_weight(weight: float) -> str:
    """Map a weight to a pastel color (green for positive, red for negative)."""
    intensity = min(abs(weight), 1.0)
    alpha = 0.2 + 0.5 * intensity
    if weight >= 0:
        return f"rgba(46, 204, 113, {alpha:.2f})"  # green
    return f"rgba(231, 76, 60, {alpha:.2f})"  # red


def highlight_tokens(text: str, token_scores: TokenScores) -> str:
    """Return HTML string with tokens (including n-grams) highlighted based on their weights."""
    tokens = [(tok, weight) for tok, weight in token_scores if tok.strip()]
    if not tokens:
        return text

    # Sort longer n-grams first to avoid nested replacements breaking spans
    tokens = sorted(tokens, key=lambda t: len(t[0]), reverse=True)
    highlighted = text
    for token, weight in tokens:
        color = _color_from_weight(weight)
        pattern = re.compile(re.escape(token), flags=re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f"<span style='background-color:{color}; padding:2px 4px; border-radius:4px'>{m.group(0)}</span>",
            highlighted,
        )
    return highlighted
