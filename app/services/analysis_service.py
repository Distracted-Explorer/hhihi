"""End-to-end analysis pipeline: OCR -> detect -> dedupe -> LLM -> store."""
from __future__ import annotations

import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.database.repository import QuestionRepository
from app.schemas.question import AnalyzeResponse
from app.services.llm_service import LLMService
from app.services.ocr_service import OCRService
from app.services.question_detector import detect_question
from app.utils.hashing import similarity, text_hash
from app.utils.image import save_image, validate_and_compress
from app.utils.lru_cache import AsyncLRUCache

logger = get_logger(__name__)

# In-memory recent-question cache (hash -> AnalyzeResponse dict)
_cache: AsyncLRUCache[str, dict] = AsyncLRUCache(max_size=settings.cache_size)


class AnalysisService:
    @staticmethod
    async def analyze(image_bytes: bytes, session: AsyncSession) -> AnalyzeResponse:
        start = time.perf_counter()

        # Validate + compress
        compressed, ext = validate_and_compress(image_bytes)
        image_path = save_image(compressed, ext, settings.temp_image_dir)

        # OCR
        extracted = await OCRService.extract_text(compressed)

        is_question, question_text = detect_question(extracted)
        if not is_question:
            elapsed = time.perf_counter() - start
            return AnalyzeResponse(
                extracted_text=extracted,
                detected_question=None,
                generated_answer=None,
                processing_time=round(elapsed, 3),
                cached=False,
                is_question=False,
            )

        # Duplicate detection: exact hash, then fuzzy similarity
        h = text_hash(question_text)
        cached = await _cache.get(h)
        if cached is None:
            for k, v in await _cache.items():
                if similarity(v["detected_question"], question_text) >= settings.similarity_threshold:
                    cached = v
                    break

        if cached is not None:
            elapsed = time.perf_counter() - start
            logger.info("Cache hit for question hash=%s", h[:8])
            return AnalyzeResponse(
                id=cached.get("id"),
                extracted_text=extracted,
                detected_question=question_text,
                generated_answer=cached["generated_answer"],
                processing_time=round(elapsed, 3),
                cached=True,
                is_question=True,
            )

        # Also check DB for prior identical hash
        repo = QuestionRepository(session)
        prior = await repo.find_by_hash(h)
        if prior is not None:
            elapsed = time.perf_counter() - start
            payload = {
                "id": prior.id,
                "detected_question": prior.detected_question,
                "generated_answer": prior.generated_answer,
            }
            await _cache.set(h, payload)
            return AnalyzeResponse(
                id=prior.id,
                extracted_text=extracted,
                detected_question=question_text,
                generated_answer=prior.generated_answer,
                processing_time=round(elapsed, 3),
                cached=True,
                is_question=True,
            )

        # LLM
        answer = await LLMService.answer(question_text)
        elapsed = time.perf_counter() - start

        record = await repo.create(
            image_path=image_path,
            extracted_text=extracted,
            detected_question=question_text,
            generated_answer=answer,
            text_hash=h,
            processing_time_ms=int(elapsed * 1000),
        )

        await _cache.set(
            h,
            {
                "id": record.id,
                "detected_question": question_text,
                "generated_answer": answer,
            },
        )

        return AnalyzeResponse(
            id=record.id,
            extracted_text=extracted,
            detected_question=question_text,
            generated_answer=answer,
            processing_time=round(elapsed, 3),
            cached=False,
            is_question=True,
        )
