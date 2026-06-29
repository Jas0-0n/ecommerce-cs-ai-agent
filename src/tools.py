# src/tools.py
from typing import Callable
from src.llm_client import ToolDef
from src.knowledge_base import FAQKnowledgeBase

kb = FAQKnowledgeBase()


def search_faq_handler(query: str, top_k: int = 3) -> str:
    """Search the FAQ knowledge base"""
    results = kb.search(query, top_k=top_k)
    context = kb.format_context(results)
    return context


# Tool definitions (can be dynamically extended later)
FAQ_TOOLS = [
    ToolDef(
        name="search_faq",
        description="Search the e-commerce FAQ knowledge base to get official answers to common questions",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords for the question"
                }
            },
            "required": ["query"]
        },
        handler=search_faq_handler
    )
]

# Tool lookup table
TOOL_MAP: dict[str, Callable] = {t.name: t.handler for t in FAQ_TOOLS}
