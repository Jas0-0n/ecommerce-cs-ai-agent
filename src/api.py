import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from src.dispatcher import Dispatcher
from src.models import ChatRequest, ChatResponse
from src.config import settings

app = FastAPI(
    title="电商客服 AI Agent API",
    description="FAQ问答 & 投诉处理",
    version="2.0.0"
)

dispatcher = Dispatcher()

# In-memory session store: session_id -> list of {role, content}
sessions: dict[str, list[dict]] = {}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}"

    # Manage session history
    if session_id not in sessions:
        sessions[session_id] = []
    history = sessions[session_id]
    history.append({"role": "user", "content": request.message})

    # Trim history
    max_turns = settings.max_history_turns
    if len(history) > max_turns * 2:
        sessions[session_id] = history[-(max_turns * 2):]
        history = sessions[session_id]

    result = await dispatcher.handle(request.message)

    # Store assistant response
    response_text = result.get("response", "")
    history.append({"role": "assistant", "content": response_text})

    if result["route"] == "faq":
        return ChatResponse(
            session_id=session_id,
            route="faq",
            response=response_text
        )
    elif result["route"] == "complaint":
        return ChatResponse(
            session_id=session_id,
            route="complaint",
            response=response_text,
            case_id=result.get("case_id"),
            escalated=result.get("type") == "escalate"
        )
    else:
        return ChatResponse(
            session_id=session_id,
            route="agent",
            response=response_text
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint — returns Server-Sent Events."""
    session_id = request.session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}"

    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": "user", "content": request.message})

    async def generate():
        full_response = ""
        async for chunk in dispatcher.handle_stream(request.message):
            if isinstance(chunk, str):
                full_response += chunk
                yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
        sessions[session_id].append({"role": "assistant", "content": full_response})

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for a session."""
    history = sessions.get(session_id, [])
    return {"session_id": session_id, "messages": history}
