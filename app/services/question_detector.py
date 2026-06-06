"""Heuristic question detection for OCR output."""
from __future__ import annotations

import re

QUESTION_WORDS = {
    "what", "why", "how", "when", "where", "who", "which",
    "whose", "whom", "is", "are", "do", "does", "did", "can",
    "could", "should", "would", "will", "shall", "may", "might",
    "find", "solve", "calculate", "evaluate", "compute", "choose",
    "select", "identify", "determine",
}
MCQ_PATTERN = re.compile(r"(?m)^\s*(\(?[a-dA-D1-4][\)\.\:])\s+\S+")
MATH_PATTERN = re.compile(r"[\d]+\s*[\+\-\*\/=]\s*[\d]+|\b[xyz]\s*=|\bsqrt\(|\^\d")
MIN_CHARS = 8


def detect_question(text: str) -> tuple[bool, str]:
    """Return (is_question, normalized_question_text)."""
    if not text or len(text.strip()) < MIN_CHARS:
        return False, ""

    stripped = text.strip()
    lower = stripped.lower()
    first_word = lower.split()[0] if lower.split() else ""

    is_q = (
        "?" in stripped
        or first_word in QUESTION_WORDS
        or bool(MCQ_PATTERN.search(stripped))
        or bool(MATH_PATTERN.search(stripped))
    )
    return is_q, stripped
