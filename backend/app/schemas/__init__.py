"""
Schema definitions for BIWOCO AI Customer Support Chatbot
"""

from .conversation import ConversationCreate, ConversationUpdate, ConversationResponse
from .message import MessageCreate, MessageResponse, MessageUpdate
from .user import UserCreate, UserUpdate, User, UserResponse
from .knowledge import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate

# Create aliases for backward compatibility
Conversation = ConversationResponse
Message = MessageResponse

__all__ = [
    "ConversationCreate",
    "ConversationUpdate", 
    "ConversationResponse",
    "Conversation",
    "MessageCreate",
    "MessageResponse",
    "MessageUpdate",
    "Message",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "User",
    "KnowledgeBase",
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate"
]
