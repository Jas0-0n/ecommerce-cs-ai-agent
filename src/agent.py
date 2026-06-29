import json
from src.llm_client import LLMClient, Message
from src.tools import FAQ_TOOLS, TOOL_MAP

FAQ_SYSTEM_PROMPT = """你是一个电商客服AI助手，负责回答客户的常见问题。

【规则】
1. 先使用 search_faq 工具查询知识库，不要凭空回答
2. 根据知识库内容回答，引用来源
3. 语气友好专业
4. 如果知识库没有答案，引导客户联系人工客服
5. 不要提供电商服务范围之外的建议
6. 回答结尾询问"请问还有其他问题吗？"

【回答格式】
- 简洁直接回答
- 步骤类问题用编号列表
- 避免过长的回复

【示例】
用户：退货要什么条件？
回答：根据退货政策，收货后7天内可申请无理由退货，商品需保持原包装完好、未拆封使用。部分商品不适用（如定制类、生鲜类、数字商品）。请问还有其他问题吗？

用户：物流大概几天到？
回答：普通快递一般3-5个工作日送达，偏远地区可能需要5-7天。京东自营商品支持次日达/当日达服务。请问还有其他问题吗？
"""


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

            # Execute tool
            messages.append(Message(
                role="assistant",
                content=msg.content or "",
                tool_calls=msg.tool_calls
            ))

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                args = json.loads(tc.function.arguments)
                handler = TOOL_MAP.get(tool_name)
                result = handler(**args) if handler else f"未知工具: {tool_name}"

                messages.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=tc.id
                ))

        return "抱歉，暂时无法回答您的问题，请联系人工客服。"

    async def answer_stream(self, question: str, max_turns: int = 5):
        """Streaming version — yields content chunks."""
        messages = [
            Message(role="system", content=FAQ_SYSTEM_PROMPT),
            Message(role="user", content=question)
        ]

        for turn in range(max_turns):
            last_msg = None
            for chunk in self.llm.chat_stream(messages, tools=FAQ_TOOLS):
                last_msg = chunk
                if isinstance(chunk, str):
                    yield chunk

            if last_msg is None:
                yield "抱歉，暂时无法回答您的问题。"
                return

            # Check if tool calls were made
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                messages.append(Message(
                    role="assistant",
                    content=last_msg.content or "",
                    tool_calls=last_msg.tool_calls
                ))
                for tc in last_msg.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    handler = TOOL_MAP.get(tool_name)
                    result = handler(**args) if handler else f"未知工具: {tool_name}"
                    messages.append(Message(
                        role="tool",
                        content=result,
                        tool_call_id=tc.id
                    ))
                continue  # next turn with tool results
            else:
                return  # done, content already yielded

        yield "抱歉，暂时无法回答您的问题，请联系人工客服。"


COMPLAIN_SYSTEM_PROMPT = """你是一个电商投诉处理AI助手。

【流程】
1. 先共情安抚客户："非常抱歉给您带来了不好的体验"
2. 根据投诉内容，查找相关信息提供解决方案
3. 提供具体解决方案（退款/补偿/换货）
4. 如果客户不接受方案且情绪仍然负面，建议转人工

【处理原则】
- 先处理情绪，再处理问题
- 不推卸责任、不找借口
- 补偿上限：50元店铺优惠券（超出需转人工）
- 所有投诉必须记录追踪编号
- 涉及支付、法律、个人信息的问题必须转人工

【回复结构】
1. 道歉和共情
2. 简述理解的问题（确认理解正确）
3. 提出解决方案
4. 说明后续步骤
5. 询问是否满意此方案

【示例】
用户：收到的东西是坏的！
回复：非常抱歉给您带来了不好的体验。了解到您收到的商品存在质量问题，对此我们深感歉意。

我为您提供以下解决方案：
1. **退货退款**：我们安排上门取件，运费由我们承担，退款将在收到退货后3个工作日内到账
2. **换货**：我们立即为您重新发货，预计1-2个工作日送达

请问您倾向哪种方案？处理过程中如有任何问题，可随时联系人工客服。工单编号：CASE-XXXXXXXX
"""


class ComplainAgent:
    def __init__(self):
        self.llm = LLMClient()
        from src.complaint_workflow import ComplaintWorkflow
        self.workflow = ComplaintWorkflow()

    async def handle(self, text: str, sentiment: dict | None = None) -> dict:
        # 1. Execute workflow (pass sentiment to avoid duplicate analysis)
        case = await self.workflow.process(text, sentiment=sentiment)

        # 2. If escalation needed, return directly
        if case.escalated:
            return {
                "type": "escalate",
                "case_id": case.case_id,
                "reason": case.escalate_reason,
                "customer_text": text,
                "sentiment_score": case.sentiment_score
            }

        # 3. Use LLM to generate complaint response
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
