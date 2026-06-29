# tests/test_knowledge_base.py
def test_split_markdown_by_heading():
    from scripts.ingest_kb import split_markdown_by_heading

    text = """## Q: 如何退貨？
A: 七天鑑賞期內可退貨。

## Q: 退款時間？
A: 5-7 工作天。"""

    chunks = split_markdown_by_heading(text, "faq.md")
    assert len(chunks) == 2
    assert "退貨" in chunks[0][0]
    assert chunks[0][1]["source"] == "faq.md"


def test_search_returns_results():
    """需要先匯入資料才能跑，這裡先做結構測試"""
    from src.knowledge_base import FAQKnowledgeBase
    kb = FAQKnowledgeBase()
    # 只要不噴錯就好
    assert kb.collection.name == "ecommerce_faq"
