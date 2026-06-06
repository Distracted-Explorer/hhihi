"""LangChain-based LLM service supporting Ollama, Gemini, and OpenAI."""
from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.core.logging import get_logger
from app.prompts.qa_prompt import qa_prompt

logger = get_logger(__name__)


def _build_llm() -> BaseChatModel:
    provider = settings.llm_provider.lower()
    logger.info("Initializing LLM provider=%s model=%s", provider, settings.llm_model)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.google_api_key,
        )
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            base_url=settings.ollama_base_url,
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")


@lru_cache(maxsize=1)
def _get_chain():
    llm = _build_llm()
    return qa_prompt | llm | StrOutputParser()


class LLMService:
    @staticmethod
    async def answer(question: str) -> str:
        chain = _get_chain()
        try:
            result = await chain.ainvoke({"question": question})
            return result.strip()
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM generation failed")
            return f"[LLM error] {exc}"
