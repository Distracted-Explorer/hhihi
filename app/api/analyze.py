from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.core.security import require_api_key
from app.database import get_session
from app.schemas.question import AnalyzeResponse
from app.services.analysis_service import AnalysisService
from app.websocket import ws_manager

router = APIRouter()
logger = get_logger(__name__)

MAX_BYTES = 8 * 1024 * 1024  # 8MB


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit("30/minute")
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> AnalyzeResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 8MB)")

    try:
        result = await AnalysisService.analyze(raw, session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result.is_question and result.generated_answer:
        await ws_manager.broadcast(result.model_dump(mode="json"))

    logger.info(
        "analyze: is_question=%s cached=%s time=%.2fs",
        result.is_question,
        result.cached,
        result.processing_time,
    )
    return result
