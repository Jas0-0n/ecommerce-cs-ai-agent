"""Unit tests for LLM client."""
import pytest
from src.llm_client import LLMClient, Message


class TestLLMClientSingleton:
    def test_singleton(self):
        """Two instances should be the same object."""
        a = LLMClient()
        b = LLMClient()
        assert a is b

    def test_fake_mode(self):
        """Should be in fake mode when API key is default."""
        from src.config import settings
        is_fake = settings.llm_api_key in (None, "", "sk-...")
        client = LLMClient()
        assert client._fake_mode == is_fake


class TestFakeReply:
    def test_dispatch_route(self):
        client = LLMClient()
        msgs = [
            Message(role="system", content="你是一个分流系统 dispatch"),
            Message(role="user", content="退货要什么条件")
        ]
        resp = client.chat(msgs)
        assert resp.content is not None

    def test_complaint_detection(self):
        """In fake mode, complaint keywords should trigger complaint route."""
        client = LLMClient()
        if not client._fake_mode:
            pytest.skip("Not in fake mode — real LLM doesn't guarantee keyword routing")
        msgs = [
            Message(role="system", content="分流系统"),
            Message(role="user", content="东西太烂了我要投诉")
        ]
        resp = client.chat(msgs)
        assert "complaint" in resp.content
