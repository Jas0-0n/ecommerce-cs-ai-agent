import json
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
    """Singleton LLM client — reuses one OpenAI connection across the app."""
    _instance: "LLMClient | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.model = settings.llm_model
        self._fake_mode = settings.llm_api_key in (None, "", "sk-...")

        if not self._fake_mode:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
            self.async_client = AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )

    def _fake_reply(self, messages: list[Message], tools=None) -> FakeMessage:
        """Return a simulated LLM reply so the flow works during development"""
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        last_system = next((m.content for m in messages if m.role == "system"), "")

        # Check for complaint keywords
        complaint_keywords = ["投诉", "太慢", "很差", "烂", "瑕疵", "坏的", "诈骗",
                              "等了一周", "等了很久", "质量差", "不满意"]
        has_complaint = any(kw in last_user for kw in complaint_keywords)

        # High-risk keywords (should escalate)
        escalate_keywords = ["报警", "律师", "起诉", "消协", "12315", "曝光", "媒体"]
        has_escalate = any(kw in last_user for kw in escalate_keywords)

        if "sentiment" in last_system.lower() or "情感分析" in last_system:
            score = -0.8 if has_escalate else (-0.5 if has_complaint else 0.0)
            urgency = "high" if has_escalate else ("medium" if has_complaint else "low")
            intent = "complaint" if (has_complaint or has_escalate) else "faq"
            return FakeMessage(json.dumps({
                "sentiment_score": score,
                "urgency": urgency,
                "intent": intent,
                "reason": "高风险投诉" if has_escalate else ("客户投诉" if has_complaint else "一般咨询")
            }))
        elif "dispatch" in last_system.lower() or "分流" in last_system.lower():
            route = "complaint" if has_complaint else ("agent" if has_escalate else "faq")
            return FakeMessage(json.dumps({
                "route": route,
                "reason": "检测到投诉" if has_complaint else "一般咨询",
                "confidence": 0.9
            }))
        else:
            return FakeMessage(f"这是模拟回复。您的消息「{last_user[:30]}」已收到，将由客服团队处理。")

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

    def chat_stream(self, messages: list[Message], tools: list[ToolDef] | None = None):
        """Streaming synchronous call — yields content chunks."""
        if self._fake_mode:
            fake = self._fake_reply(messages, tools)
            yield fake
            return

        kwargs = {
            "model": self.model,
            "messages": [asdict(m) for m in messages],
            "stream": True,
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

        full_content = ""
        tool_calls_acc = {}

        for chunk in self.client.chat.completions.create(**kwargs):
            delta = chunk.choices[0].delta
            if delta.content:
                full_content += delta.content
                yield delta.content
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {
                            "id": tc.id or "",
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.id:
                        tool_calls_acc[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_acc[idx]["function"]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls_acc[idx]["function"]["arguments"] += tc.function.arguments

        # If tool calls were made, yield a final wrapper object
        if tool_calls_acc:
            # Build tool call objects for the agent loop
            tc_list = []
            for idx in sorted(tool_calls_acc.keys()):
                tc = tool_calls_acc[idx]
                tc_obj = type("ToolCall", (), {
                    "id": tc["id"],
                    "type": "function",
                    "function": type("Func", (), {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    })()
                })()
                tc_list.append(tc_obj)
            msg = type("StreamMsg", (), {"content": full_content, "tool_calls": tc_list})()
            yield msg

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

    async def async_chat_stream(self, messages: list[Message], tools: list[ToolDef] | None = None):
        """Async streaming version — yields content chunks."""
        if self._fake_mode:
            fake = self._fake_reply(messages, tools)
            yield fake
            return

        kwargs = {
            "model": self.model,
            "messages": [asdict(m) for m in messages],
            "stream": True,
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

        full_content = ""
        tool_calls_acc = {}

        async for chunk in await self.async_client.chat.completions.create(**kwargs):
            delta = chunk.choices[0].delta
            if delta.content:
                full_content += delta.content
                yield delta.content
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {
                            "id": tc.id or "",
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.id:
                        tool_calls_acc[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_acc[idx]["function"]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls_acc[idx]["function"]["arguments"] += tc.function.arguments

        if tool_calls_acc:
            tc_list = []
            for idx in sorted(tool_calls_acc.keys()):
                tc = tool_calls_acc[idx]
                tc_obj = type("ToolCall", (), {
                    "id": tc["id"],
                    "type": "function",
                    "function": type("Func", (), {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    })()
                })()
                tc_list.append(tc_obj)
            msg = type("StreamMsg", (), {"content": full_content, "tool_calls": tc_list})()
            yield msg
