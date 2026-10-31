from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.services.chatbot.assistant import assistant

router = APIRouter(prefix="/assistant", tags=["AI Shopping Assistant"])

class ChatRequest(BaseModel):
    message: str
    history: Optional[list[dict]] = []

class KeyConfigRequest(BaseModel):
    api_key: str

@router.post("/chat")
def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = assistant.process_query(db, req.message, req.history)
    return result

@router.get("/config")
def get_assistant_config():
    is_gemini_active = bool(assistant.api_key)
    return {
        "gemini_configured": is_gemini_active,
        "active_mode": "gemini_cloud" if is_gemini_active else "local_fallback",
        "description": "Scrollix uses local AI by default. Add an optional free Gemini API key for enhanced conversational fluency."
    }

@router.post("/config")
def update_assistant_config(req: KeyConfigRequest):
    assistant.set_api_key(req.api_key)
    return {
        "success": True,
        "gemini_configured": bool(assistant.api_key),
        "message": "Assistant API key updated successfully."
    }
