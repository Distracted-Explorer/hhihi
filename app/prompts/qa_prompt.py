"""LangChain prompt templates."""
from langchain_core.prompts import ChatPromptTemplate

QA_SYSTEM = (
    "You are an intelligent question-solving assistant. "
    "Analyze the extracted question carefully and answer concisely."
)

QA_HUMAN = (
    "Analyze the extracted question carefully.\n\n"
    "Provide:\n"
    "Final Answer\n"
    "Short Explanation\n\n"
    "Question:\n{question}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [("system", QA_SYSTEM), ("human", QA_HUMAN)]
)
