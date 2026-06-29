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
    handler: Callable  # 實際執行函式


class FakeMessage:
    """模擬的 OpenAI 回覆，用於開發時無需 API key"""
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
        """回傳模擬的 LLM 回覆，讓開發時能跑流程"""
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        last_system = next((m.content for m in messages if m.role == "system"), "")

        # 判斷客訴關鍵字
        complaint_keywords = ["客訴", "太慢", "很差", "很爛", "瑕疵", "壞的", "詐騙",
                              "等了一個禮拜", "等了一週", "投訴", "不滿"]
        has_complaint = any(kw in last_user for kw in complaint_keywords)

        # 高風險關鍵字（應升級）
        escalate_keywords = ["找記者", "告你", "告", "報警", "找主管", "叫主管", "主管", "消基會", "法律途徑"]
        has_escalate = any(kw in last_user for kw in escalate_keywords)

        if "情緒分析" in last_system:
            score = -0.8 if has_escalate else (-0.5 if has_complaint else 0.0)
            urgency = "high" if has_escalate else ("medium" if has_complaint else "low")
            intent = "complaint" if (has_complaint or has_escalate) else "faq"
            return FakeMessage(json.dumps({
                "sentiment_score": score,
                "urgency": urgency,
                "intent": intent,
                "reason": "高風險客訴" if has_escalate else ("客戶抱怨" if has_complaint else "一般查詢")
            }))
        elif "分流系統" in last_system:
            route = "complaint" if has_complaint else ("agent" if has_escalate else "faq")
            return FakeMessage(json.dumps({
                "route": route,
                "reason": "偵測到客訴內容" if has_complaint else "一般查詢",
                "confidence": 0.9
            }))
        else:
            return FakeMessage(f"這是模擬回覆。您的問題：「{last_user[:30]}」已收到，將由客服團隊處理。")

    def chat(self, messages: list[Message], tools: list[ToolDef] | None = None):
        """同步呼叫，回傳 assistant 回覆"""
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
        """非同步版本"""
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
