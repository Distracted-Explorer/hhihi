"""EasyOCR-based text extraction service."""
from __future__ import annotations

import asyncio
import io
import re
from typing import Any

import numpy as np
from PIL import Image

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OCRService:
    """Lazy-initialized EasyOCR wrapper, run off the event loop."""

    _reader: Any | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def _get_reader(cls) -> Any:
        if cls._reader is None:
            async with cls._lock:
                if cls._reader is None:
                    import easyocr  # heavy import — defer

                    logger.info(
                        "Initializing EasyOCR reader (langs=%s, gpu=%s)",
                        settings.ocr_lang_list,
                        settings.ocr_gpu,
                    )
                    cls._reader = await asyncio.to_thread(
                        easyocr.Reader,
                        settings.ocr_lang_list,
                        gpu=settings.ocr_gpu,
                        verbose=False,
                    )
        return cls._reader

    @staticmethod
    def _clean_text(text: str) -> str:
        # Collapse whitespace, strip stray symbols at edges
        text = re.sub(r"[\u200b\u200c\ufeff]", "", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)
        # Remove isolated single-char noise on a line
        lines = [l.strip(" -•|") for l in text.splitlines() if l.strip()]
        return "\n".join(lines).strip()

    @classmethod
    async def extract_text(cls, image_bytes: bytes) -> str:
        reader = await cls._get_reader()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)

        def _run() -> str:
            results = reader.readtext(arr, detail=0, paragraph=True)
            return "\n".join(results)

        raw = await asyncio.to_thread(_run)
        cleaned = cls._clean_text(raw)
        logger.debug("OCR extracted %d chars", len(cleaned))
        return cleaned
