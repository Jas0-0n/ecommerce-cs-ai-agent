# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_api_key: str = "sk-..."
    llm_base_url: Optional[str] = None  # 可接 Ollama 或其他 proxy
    llm_model: str = "gpt-4o"

    # Knowledge Base
    kb_collection_name: str = "ecommerce_faq"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Complain
    escalate_keywords: list = ["消基會", "找記者", "告你", "法律途徑", "找主管", "叫主管"]
    auto_resolve_sentiment_threshold: float = -0.3  # 低於此分數強制轉人工

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
