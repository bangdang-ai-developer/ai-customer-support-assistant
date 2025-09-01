"""
WebSocket endpoint for real-time chat communication
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.models.message import Message
from app.models.conversation import Conversation, MessageRole
from app.services.ai_service import AIService
from uuid import uuid4

class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_conversation(self, message: str, conversation_id: str):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    db: Session
):
    """
    WebSocket endpoint for real-time chat
    
    Message types:
    - user_message: User sends a message
    - ai_response_start: AI starts generating response
    - ai_response_complete: AI completes response
    - typing_indicator: Show typing indicator
    - error: Error occurred
    """
    await manager.connect(websocket, conversation_id)
    
    # Send initial connection confirmation
    await websocket.send_text(json.dumps({
        "type": "connection_established",
        "conversation_id": conversation_id,
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    try:
        # Initialize AI service
        ai_service = AIService()
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "user_message":
                # Save user message to database
                user_message = Message(
                    id=str(uuid4()),
                    conversation_id=conversation_id,
                    role=MessageRole.USER,
                    content=message_data["content"],
                    msg_metadata=message_data.get("metadata", {})
                )
                db.add(user_message)
                db.commit()
                
                # Broadcast user message to all connected clients
                await manager.broadcast_to_conversation(
                    json.dumps({
                        "type": "new_message",
                        "message": {
                            "id": str(user_message.id),
                            "role": "USER",
                            "content": user_message.content,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }),
                    conversation_id
                )
                
                # Send typing indicator
                await manager.broadcast_to_conversation(
                    json.dumps({
                        "type": "ai_response_start",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    conversation_id
                )
                
                # Generate AI response
                try:
                    # Get conversation context
                    conversation = db.query(Conversation).filter(
                        Conversation.id == conversation_id
                    ).first()
                    
                    # Get recent messages for context
                    recent_messages = db.query(Message).filter(
                        Message.conversation_id == conversation_id
                    ).order_by(Message.created_at.desc()).limit(10).all()
                    
                    # Generate response using AI service with RAG support
                    ai_response = await ai_service.generate_response(
                        user_message.content,
                        conversation.scenario_type if conversation else "ECOMMERCE",
                        [{"role": msg.role.value, "content": msg.content} 
                         for msg in reversed(recent_messages)],
                        db  # Enable RAG by passing database session
                    )
                    
                    # Save AI response to database
                    ai_message = Message(
                        id=str(uuid4()),
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=ai_response.content,
                        msg_metadata={
                            "model": ai_response.model,
                            "tokens": ai_response.tokens_used or 0,
                            "confidence": ai_response.confidence or 0.0
                        }
                    )
                    db.add(ai_message)
                    db.commit()
                    
                    # Send AI response
                    await manager.broadcast_to_conversation(
                        json.dumps({
                            "type": "ai_response_complete",
                            "response": {
                                "id": str(ai_message.id),
                                "role": "ASSISTANT",
                                "content": ai_message.content,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        }),
                        conversation_id
                    )
                    
                except Exception as e:
                    # Send error message if AI generation fails
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Failed to generate AI response",
                        "details": str(e)
                    }))
            
            elif message_data["type"] == "typing_indicator":
                # Broadcast typing indicator to other clients
                await manager.broadcast_to_conversation(
                    json.dumps({
                        "type": "typing_indicator",
                        "user_id": message_data.get("user_id"),
                        "is_typing": message_data.get("is_typing", False)
                    }),
                    conversation_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        # Notify other clients about disconnection
        await manager.broadcast_to_conversation(
            json.dumps({
                "type": "user_disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }),
            conversation_id
        )
    except Exception as e:
        manager.disconnect(websocket, conversation_id)