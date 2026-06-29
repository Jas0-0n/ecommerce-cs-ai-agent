# src/models.py
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    platform: Optional[str] = "api"  # web, line, telegram


class ChatResponse(BaseModel):
    session_id: str
    route: str  # faq | complaint | agent
    response: str
    case_id: Optional[str] = None
    escalated: Optional[bool] = None
