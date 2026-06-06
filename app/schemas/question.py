"""Pydantic API schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    id: int | None = None
    extracted_text: str
    detected_question: str | None
    generated_answer: str | None
    processing_time: float = Field(description="Processing time in seconds")
    cached: bool = False
    is_question: bool = True


class HealthResponse(BaseModel):
    status: str = "ok"
    llm_provider: str
    version: str = "1.0.0"


class HistoryItem(BaseModel):
    id: int
    extracted_text: str
    detected_question: str
    generated_answer: str
    processing_time_ms: int
    timestamp: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    count: int
