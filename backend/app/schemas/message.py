"""Message schemas"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.models.conversation import MessageRole

class MessageBase(BaseModel):
    role: MessageRole
    content: str
    msg_metadata: Optional[Dict[str, Any]] = {}

class MessageCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    msg_metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    msg_metadata: Optional[Dict[str, Any]] = {}
    tokens_used: Optional[int] = None
    response_time: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageFeedbackResponse(BaseModel):
    rating: int
    comment: Optional[str] = None
    
    class Config:
        from_attributes = True

class MessageWithFeedback(MessageResponse):
    feedback: Optional[MessageFeedbackResponse] = None
