"""
LLM 工厂：支持 Ollama / OpenAI 兼容 API
"""
from langchain_community.llms import Ollama
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import BaseLLM
from config import (
    LLM_PROVIDER, OPENAI_API_KEY, OPENAI_BASE_URL,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)


def get_llm() -> BaseLLM:
    if LLM_PROVIDER.lower() == "ollama":
        return Ollama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
        )
    if LLM_PROVIDER.lower() in ("openai", "openai_compatible"):
        return ChatOpenAI(
            api_key=OPENAI_API_KEY or "dummy",
            base_url=OPENAI_BASE_URL or None,
            model="gpt-3.5-turbo",
            temperature=0.1,
        )
    raise ValueError(f"不支持的 LLM_PROVIDER: {LLM_PROVIDER}")
