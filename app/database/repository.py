"""Repository pattern for question records."""
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import QuestionRecord


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **fields) -> QuestionRecord:
        record = QuestionRecord(**fields)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get(self, record_id: int) -> QuestionRecord | None:
        return await self.session.get(QuestionRecord, record_id)

    async def find_by_hash(self, text_hash: str) -> QuestionRecord | None:
        stmt = select(QuestionRecord).where(QuestionRecord.text_hash == text_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 50) -> list[QuestionRecord]:
        stmt = (
            select(QuestionRecord)
            .order_by(desc(QuestionRecord.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, record_id: int) -> bool:
        record = await self.get(record_id)
        if not record:
            return False
        await self.session.delete(record)
        await self.session.commit()
        return True
