from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_api_key: str = "sk-..."
    llm_base_url: Optional[str] = None
    llm_model: str = "gpt-4o"

    # Knowledge Base
    kb_collection_name: str = "ecommerce_faq"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Complaint — only truly high-risk keywords trigger escalation
    escalate_keywords: list = [
        "报警", "110", "律师", "起诉", "法院", "法律途径",
        "消协", "12315", "12345", "工商", "市场监督",
        "曝光", "媒体", "记者", "上电视",
        "诈骗", "骗子",
    ]
    auto_resolve_sentiment_threshold: float = -0.6

    # Bot tokens (optional)
    line_channel_access_token: Optional[str] = None
    line_channel_secret: Optional[str] = None
    telegram_bot_token: Optional[str] = None

    # Session history
    max_history_turns: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
