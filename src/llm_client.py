# src/llm_client.py
import json
import os
from typing import Callable
from dataclasses import dataclass, asdict
from openai import OpenAI, AsyncOpenAI
from src.config import settings


@dataclass
class Message:
    role: str  # system | user | assistant | tool
    content: str
    tool_call_id: str | None = None
    tool_calls: list | None = None


@dataclass
class ToolDef:
    """OpenAI-compatible tool definition"""
    name: str
    description: str
    parameters: dict  # JSON schema
    handler: Callable  # Actual execution function


class FakeMessage:
    """Simulated OpenAI response, used during development without an API key"""
    def __init__(self, text: str):
        self.content = text
        self.tool_calls = None


class LLMClient:
    def __init__(self):
        self.model = settings.llm_model
        self._fake_mode = settings.llm_api_key in (None, "", "sk-...")

        if not self._fake_mode:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )
            self.async_client = AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )

    def _fake_reply(self, messages: list[Message], tools=None) -> FakeMessage:
        """Return a simulated LLM reply so the flow works during development"""
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        last_system = next((m.content for m in messages if m.role == "system"), "")

        # Check for complaint keywords
        complaint_keywords = ["complaint", "too slow", "terrible", "defective", "broken", "scam",
                              "waited a week", "waited one week", "poor quality", "unsatisfied"]
        has_complaint = any(kw in last_user.lower() for kw in complaint_keywords)

        # High-risk keywords (should escalate)
        escalate_keywords = ["sue", "lawyer", "police", "manager", "supervisor", "complaint bureau", "legal action"]
        has_escalate = any(kw in last_user.lower() for kw in escalate_keywords)

        # Also support Chinese keywords for backward compatibility
        cn_complaint_kw = ["客訴", "太慢", "很差", "很爛", "瑕疵", "壞的", "詐騙",
                          "等了一個禮拜", "等了一週", "投訴", "不滿"]
        cn_escalate_kw = ["找記者", "告你", "告", "報警", "找主管", "叫主管", "主管", "消基會", "法律途徑"]
        has_complaint = has_complaint or any(kw in last_user for kw in cn_complaint_kw)
        has_escalate = has_escalate or any(kw in last_user for kw in cn_escalate_kw)

        if "sentiment" in last_system.lower() or "情緒分析" in last_system:
            score = -0.8 if has_escalate else (-0.5 if has_complaint else 0.0)
            urgency = "high" if has_escalate else ("medium" if has_complaint else "low")
            intent = "complaint" if (has_complaint or has_escalate) else "faq"
            return FakeMessage(json.dumps({
                "sentiment_score": score,
                "urgency": urgency,
                "intent": intent,
                "reason": "High-risk complaint" if has_escalate else ("Customer complaint" if has_complaint else "General inquiry")
            }))
        elif "dispatch" in last_system.lower() or "分流" in last_system.lower() or "分流系統" in last_system:
            route = "complaint" if has_complaint else ("agent" if has_escalate else "faq")
            return FakeMessage(json.dumps({
                "route": route,
                "reason": "Complaint detected" if has_complaint else "General inquiry",
                "confidence": 0.9
            }))
        else:
            return FakeMessage(f"This is a simulated reply. Your message: 「{last_user[:30]}」has been received and will be handled by our customer service team.")

    def chat(self, messages: list[Message], tools: list[ToolDef] | None = None):
        """Synchronous call, returns assistant reply"""
        if self._fake_mode:
            return self._fake_reply(messages, tools)

        kwargs = {
            "model": self.model,
            "messages": [asdict(m) for m in messages],
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    }
                }
                for t in tools
            ]

        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message

    async def async_chat(self, messages: list[Message], tools: list[ToolDef] | None = None):
        """Async version"""
        if self._fake_mode:
            return self._fake_reply(messages, tools)

        kwargs = {
            "model": self.model,
            "messages": [asdict(m) for m in messages],
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    }
                }
                for t in tools
            ]

        resp = await self.async_client.chat.completions.create(**kwargs)
        return resp.choices[0].message
