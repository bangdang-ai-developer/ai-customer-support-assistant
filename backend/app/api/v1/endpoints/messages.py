"""
Message handling endpoints with AI integration
"""

import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.models.message import Message
from app.models.conversation import MessageRole, Conversation
from app.schemas.message import MessageCreate, MessageResponse, MessageWithFeedback
from app.services.ai_service import AIService
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    # Verify conversation exists
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create user message
    user_message = Message(
        id=str(uuid4()),
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=message_data.content,
        metadata=message_data.metadata or {}
    )
    
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Generate AI response
    start_time = time.time()
    
    ai_service = AIService()
    chat_service = ChatService(db)
    
    # Get conversation context
    context = await chat_service.get_conversation_context(conversation_id)
    
    # Generate AI response based on scenario with RAG support
    ai_response = await ai_service.generate_response(
        message=message_data.content,
        scenario_type=conversation.scenario_type,
        conversation_context=context,
        db=db  # Enable RAG by passing database session
    )
    
    response_time = int((time.time() - start_time) * 1000)  # milliseconds
    
    # Create AI message
    ai_message = Message(
        id=str(uuid4()),
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=ai_response.content,
        metadata={
            "model": ai_response.model,
            "tokens_used": ai_response.tokens_used,
            "confidence": ai_response.confidence
        },
        tokens_used=ai_response.tokens_used,
        response_time=response_time
    )
    
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return ai_message


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get conversation messages"""
    # Verify conversation exists
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).offset(skip).limit(limit).all()
    
    return messages


@router.get("/messages/{message_id}", response_model=MessageWithFeedback)
async def get_message(
    message_id: str,
    db: Session = Depends(get_db)
):
    """Get message with feedback"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    return message


# @router.put("/messages/{message_id}/feedback")
# async def add_message_feedback(
#     message_id: str,
#     feedback_data: dict,
#     db: Session = Depends(get_db)
# ):
#     """Add feedback to a message - temporarily disabled"""
#     # from app.models.message import MessageFeedback, FeedbackRating
#     
#     message = db.query(Message).filter(Message.id == message_id).first()
#     
#     if not message:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Message not found"
#         )
#     
#     # Create feedback
#     # feedback = MessageFeedback(
#     #     id=str(uuid4()),
#     #     message_id=message_id,
#     #     user_id=feedback_data.get("user_id"),
#     #     rating=FeedbackRating(feedback_data["rating"]),
#     #     comment=feedback_data.get("comment")
#     # )
    
    # db.add(feedback)
    # db.commit()
    
    return {"message": "Feedback feature temporarily disabled"}