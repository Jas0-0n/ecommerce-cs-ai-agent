# src/agent.py
import json
from src.llm_client import LLMClient, Message
from src.tools import FAQ_TOOLS, TOOL_MAP

FAQ_SYSTEM_PROMPT = """你是電商客服 AI 助理，負責回答顧客的 FAQ 問題。

【規則】
1. 先使用 search_faq 工具查詢知識庫，不要憑空回答
2. 根據知識庫內容回答，引用來源
3. 回答要親切、專業，使用繁體中文
4. 若知識庫找不到答案，引導顧客聯繫人工客服
5. 不要提供任何超出電商服務範圍的建議
6. 回答結尾可以問「還有其他問題嗎？」

【回答格式】
- 簡潔直接回答問題
- 必要時條列步驟（如退貨流程）
- 避免過長的回覆"""


class FAQAgent:
    def __init__(self):
        self.llm = LLMClient()

    async def answer(self, question: str, max_turns: int = 5) -> str:
        messages = [
            Message(role="system", content=FAQ_SYSTEM_PROMPT),
            Message(role="user", content=question)
        ]

        for turn in range(max_turns):
            msg = self.llm.chat(messages, tools=FAQ_TOOLS)

            if not msg.tool_calls:
                return msg.content

            # 執行工具
            messages.append(Message(
                role="assistant",
                content=msg.content or "",
                tool_calls=msg.tool_calls
            ))

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                args = json.loads(tc.function.arguments)

                handler = TOOL_MAP.get(tool_name)
                if handler:
                    result = handler(**args)
                else:
                    result = f"未知工具: {tool_name}"

                messages.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=tc.id
                ))

        # 追加到 src/agent.py 底部

COMPLAIN_SYSTEM_PROMPT = """你是電商客訴處理 AI 助理。

【處理流程】
1. 先同理顧客情緒：「很抱歉讓您有這樣的體驗」
2. 根據客訴內容選擇相對應的工具查詢資訊
3. 提供具體解決方案（退款/補償/換貨）
4. 若顧客不接受方案且情緒持續負面，建議升級專人處理

【客訴處理原則】
- 先處理情緒，再處理事情
- 不要辯解或推卸責任
- 不要承諾超出權限的補償（最高補償金額 NTD 300 購物金）
- 所有客訴案件需記錄追蹤編號
- 涉及金流、法律、個資問題一律升級人工

【回應結構】
1. 道歉與同理
2. 簡述理解的問題（確認理解正確）
3. 提出的解決方案
4. 後續步驟說明
5. 詢問是否滿意此處理方式"""


class ComplainAgent:
    def __init__(self):
        self.llm = LLMClient()
        from src.complaint_workflow import ComplaintWorkflow
        self.workflow = ComplaintWorkflow()

    async def handle(self, text: str) -> dict:
        # 1. 執行工作流
        case = await self.workflow.process(text)

        # 2. 如果需要升級，直接返回
        if case.escalated:
            return {
                "type": "escalate",
                "case_id": case.case_id,
                "reason": case.escalate_reason,
                "customer_text": text,
                "sentiment_score": case.sentiment_score
            }

        # 3. 用 LLM 生成客訴回應
        messages = [
            Message(role="system", content=COMPLAIN_SYSTEM_PROMPT),
            Message(role="user", content=text)
        ]
        response = self.llm.chat(messages)
        case.auto_response = response.content

        return {
            "type": "auto_reply",
            "case_id": case.case_id,
            "response": response.content,
            "sentiment_score": case.sentiment_score,
            "urgency": case.urgency
        }
