"""
WebSocket manager for real-time chat communication
"""

from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        # Store active connections by conversation_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Accept WebSocket connection and add to conversation room"""
        await websocket.accept()
        
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        
        self.active_connections[conversation_id].append(websocket)
        
        logger.info(f"WebSocket connected to conversation {conversation_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to chat",
            "conversation_id": conversation_id
        }, conversation_id)
    
    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Remove WebSocket connection from conversation room"""
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
                
                # Clean up empty conversation rooms
                if not self.active_connections[conversation_id]:
                    del self.active_connections[conversation_id]
                
                logger.info(f"WebSocket disconnected from conversation {conversation_id}")
    
    async def send_personal_message(self, message: dict, conversation_id: str):
        """Send message to all connections in a conversation"""
        if conversation_id in self.active_connections:
            disconnected_websockets = []
            
            for websocket in self.active_connections[conversation_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    disconnected_websockets.append(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, conversation_id)
    
    async def broadcast_typing_indicator(self, conversation_id: str, is_typing: bool, user_id: str = None):
        """Send typing indicator to conversation participants"""
        message = {
            "type": "typing_indicator",
            "conversation_id": conversation_id,
            "is_typing": is_typing,
            "user_id": user_id
        }
        
        await self.send_personal_message(message, conversation_id)
    
    async def broadcast_new_message(self, conversation_id: str, message_data: dict):
        """Broadcast new message to conversation participants"""
        websocket_message = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": message_data
        }
        
        await self.send_personal_message(websocket_message, conversation_id)
    
    async def broadcast_ai_response_start(self, conversation_id: str):
        """Notify that AI is generating a response"""
        message = {
            "type": "ai_response_start",
            "conversation_id": conversation_id,
            "message": "AI is typing..."
        }
        
        await self.send_personal_message(message, conversation_id)
    
    async def broadcast_ai_response_complete(self, conversation_id: str, response_data: dict):
        """Broadcast completed AI response"""
        message = {
            "type": "ai_response_complete",
            "conversation_id": conversation_id,
            "response": response_data
        }
        
        await self.send_personal_message(message, conversation_id)
    
    def get_conversation_connection_count(self, conversation_id: str) -> int:
        """Get number of active connections for a conversation"""
        return len(self.active_connections.get(conversation_id, []))
    
    def get_total_connections(self) -> int:
        """Get total number of active WebSocket connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_active_conversations(self) -> List[str]:
        """Get list of conversation IDs with active connections"""
        return list(self.active_connections.keys())