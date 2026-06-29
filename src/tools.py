"""Tool definitions with lazy knowledge base initialization."""
from typing import Callable
from src.llm_client import ToolDef

# Lazy-loaded KB singleton — avoids loading embedding model at import time
_kb = None


def _get_kb():
    global _kb
    if _kb is None:
        from src.knowledge_base import FAQKnowledgeBase
        _kb = FAQKnowledgeBase()
    return _kb


def search_faq_handler(query: str, top_k: int = 3) -> str:
    """Search the FAQ knowledge base"""
    kb = _get_kb()
    results = kb.search(query, top_k=top_k)
    context = kb.format_context(results)
    return context


# Tool definitions
FAQ_TOOLS = [
    ToolDef(
        name="search_faq",
        description="搜索电商FAQ知识库，获取常见问题的官方解答。适用于退货、物流、支付、售后等问题。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，例如：退货条件、物流时效、支付方式"
                }
            },
            "required": ["query"]
        },
        handler=search_faq_handler
    )
]

# Tool lookup table
TOOL_MAP: dict[str, Callable] = {t.name: t.handler for t in FAQ_TOOLS}
