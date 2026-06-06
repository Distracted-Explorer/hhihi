from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_api_key
from app.database import get_session
from app.database.repository import QuestionRepository
from app.schemas.question import HistoryItem, HistoryResponse

router = APIRouter()


@router.get(
    "/history",
    response_model=HistoryResponse,
    dependencies=[Depends(require_api_key)],
)
async def history(
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> HistoryResponse:
    repo = QuestionRepository(session)
    records = await repo.list_recent(limit=limit)
    items = [HistoryItem.model_validate(r) for r in records]
    return HistoryResponse(items=items, count=len(items))
