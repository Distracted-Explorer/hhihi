"""Text normalization, hashing, and similarity helpers."""
import hashlib
import re
from difflib import SequenceMatcher

_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s\?\=\+\-\*\/\(\)\.\,]")


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()
