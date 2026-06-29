# src/api.py
import uuid
from fastapi import FastAPI
from src.dispatcher import Dispatcher
from src.models import ChatRequest, ChatResponse

app = FastAPI(
    title="電商客服 AI Agent API",
    description="FAQ 問答 & 客訴處理",
    version="1.0.0"
)

dispatcher = Dispatcher()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}"

    result = await dispatcher.handle(request.message)

    if result["route"] == "faq":
        return ChatResponse(
            session_id=session_id,
            route="faq",
            response=result["response"]
        )
    elif result["route"] == "complaint":
        return ChatResponse(
            session_id=session_id,
            route="complaint",
            response=result.get("response", ""),
            case_id=result.get("case_id"),
            escalated=result.get("type") == "escalate"
        )
    else:  # agent
        return ChatResponse(
            session_id=session_id,
            route="agent",
            response=result["response"]
        )


@app.get("/health")
async def health():
    return {"status": "ok"}
