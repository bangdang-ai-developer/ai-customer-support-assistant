"""
Pydantic schemas for conversation data validation and serialization
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.conversation import ScenarioType, ConversationStatus


class ConversationBase(BaseModel):
    scenario_type: str  # Support both built-in and custom scenarios
    title: Optional[str] = None
    user_id: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None


class ConversationResponse(ConversationBase):
    id: str
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True