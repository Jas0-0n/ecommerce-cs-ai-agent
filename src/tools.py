# src/tools.py
from typing import Callable
from src.llm_client import ToolDef
from src.knowledge_base import FAQKnowledgeBase

kb = FAQKnowledgeBase()


def search_faq_handler(query: str, top_k: int = 3) -> str:
    """搜尋 FAQ 知識庫"""
    results = kb.search(query, top_k=top_k)
    context = kb.format_context(results)
    return context


# 工具定義（之後會動態擴充）
FAQ_TOOLS = [
    ToolDef(
        name="search_faq",
        description="搜尋電商 FAQ 知識庫，取得常見問題的官方回答",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要搜尋的問題關鍵字"
                }
            },
            "required": ["query"]
        },
        handler=search_faq_handler
    )
]

# 工具查找表
TOOL_MAP: dict[str, Callable] = {t.name: t.handler for t in FAQ_TOOLS}
