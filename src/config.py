# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_api_key: str = "sk-..."
    llm_base_url: Optional[str] = None  # For Ollama or other proxies
    llm_model: str = "gpt-4o"

    # Knowledge Base
    kb_collection_name: str = "ecommerce_faq"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Complaint
    escalate_keywords: list = ["complaint bureau", "news reporter", "sue you", "legal action", "manager", "call manager"]
    auto_resolve_sentiment_threshold: float = -0.3  # Below this score, force human transfer

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
