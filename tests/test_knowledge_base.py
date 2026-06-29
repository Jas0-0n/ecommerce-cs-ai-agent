"""Tests for FAQ knowledge base."""
import pytest
from src.knowledge_base import FAQKnowledgeBase


class TestKnowledgeBase:
    @pytest.fixture
    def kb(self):
        return FAQKnowledgeBase(lazy_encoder=False)

    def test_search_returns_results(self, kb):
        results = kb.search("退货条件")
        assert len(results) > 0

    def test_search_format(self, kb):
        results = kb.search("退货条件")
        assert "content" in results[0]
        assert "metadata" in results[0]

    def test_format_context(self, kb):
        results = kb.search("退货条件")
        context = kb.format_context(results)
        assert "参考" in context
        assert "来源" in context

    def test_hybrid_search(self, kb):
        """Hybrid search should return results from both semantic and keyword."""
        results = kb.search("京东自营7天无理由退货")
        assert len(results) > 0
        # Should find relevant content about returns
        found = any("退货" in r["content"] or "退换" in r["content"] for r in results)
        assert found
