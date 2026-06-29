# src/agent.py
import json
from src.llm_client import LLMClient, Message
from src.tools import FAQ_TOOLS, TOOL_MAP

FAQ_SYSTEM_PROMPT = """You are an e-commerce customer service AI assistant, responsible for answering customer FAQ questions.

【Rules】
1. First use the search_faq tool to query the knowledge base, do not answer out of thin air
2. Answer based on knowledge base content, cite sources
3. Be friendly and professional
4. If the knowledge base has no answer, guide the customer to contact human customer service
5. Do not provide any advice outside the scope of e-commerce services
6. End the answer by asking "Do you have any other questions?"

【Answer Format】
- Concise and direct answers
- Use bullet points for steps when necessary (e.g., return process)
- Avoid overly long replies"""


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
                if handler:
                    result = handler(**args)
                else:
                    result = f"Unknown tool: {tool_name}"

                messages.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=tc.id
                ))

        # Appended to src/agent.py bottom

COMPLAIN_SYSTEM_PROMPT = """You are an e-commerce complaint handling AI assistant.

【Process Flow】
1. First empathize with the customer: "I'm sorry you had this experience"
2. Based on the complaint content, use the appropriate tool to look up information
3. Provide a specific solution (refund/compensation/exchange)
4. If the customer does not accept the solution and their sentiment remains negative, recommend escalation to a human agent

【Complaint Handling Principles】
- Address emotions first, then the issue
- Do not make excuses or deflect responsibility
- Do not promise compensation beyond your authority (maximum compensation NTD 300 store credit)
- All complaint cases must be recorded with a tracking ID
- Issues involving payments, legal matters, or personal data must be escalated to human agents

【Response Structure】
1. Apology and empathy
2. Brief summary of the understood issue (confirm understanding is correct)
3. Proposed solution
4. Next steps explanation
5. Ask if they are satisfied with this resolution"""


class ComplainAgent:
    def __init__(self):
        self.llm = LLMClient()
        from src.complaint_workflow import ComplaintWorkflow
        self.workflow = ComplaintWorkflow()

    async def handle(self, text: str) -> dict:
        # 1. Execute workflow
        case = await self.workflow.process(text)

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
