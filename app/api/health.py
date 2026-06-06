from fastapi import APIRouter

from app.config import settings
from app.schemas.question import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", llm_provider=settings.llm_provider)
