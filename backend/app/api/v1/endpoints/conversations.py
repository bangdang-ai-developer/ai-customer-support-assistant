"""
Conversation management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.models.conversation import Conversation, ConversationStatus, ScenarioType
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationUpdate
)

router = APIRouter()


@router.post("/start", response_model=ConversationResponse)
async def start_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Start a new conversation"""
    conversation = Conversation(
        id=str(uuid4()),
        scenario_type=conversation_data.scenario_type,
        user_id=conversation_data.user_id,
        title=conversation_data.title,
        status=ConversationStatus.ACTIVE
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation by ID"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: Optional[str] = None,
    scenario_type: Optional[ScenarioType] = None,
    status: Optional[ConversationStatus] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List conversations with optional filters"""
    query = db.query(Conversation)
    
    if user_id:
        query = query.filter(Conversation.user_id == user_id)
    if scenario_type:
        query = query.filter(Conversation.scenario_type == scenario_type)
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.offset(skip).limit(limit).all()
    return conversations


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conversation_data: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    update_data = conversation_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)
    
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}