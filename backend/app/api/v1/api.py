"""
Main API router that includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import conversations, messages, knowledge, upload, scenarios

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["conversations"]
)

api_router.include_router(
    messages.router,
    prefix="/conversations",
    tags=["messages"]
)

api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["knowledge"]
)

api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)

api_router.include_router(
    scenarios.router,
    prefix="/scenarios",
    tags=["scenarios"]
)