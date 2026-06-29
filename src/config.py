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

    # Complaint — keywords to match user input (support both languages)
    escalate_keywords: list = ["消基會", "找記者", "告你", "法律途徑", "找主管", "叫主管",
                               "complaint bureau", "sue", "lawyer", "manager"]
    auto_resolve_sentiment_threshold: float = -0.3  # Below this score, force human transfer

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
