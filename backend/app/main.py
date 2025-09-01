"""
Main FastAPI application for BIWOCO AI Customer Support Chatbot
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.utils.websocket import WebSocketManager

# Import all models to ensure they are registered
from app.models import User, Conversation, Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="BIWOCO AI Customer Support Chatbot API",
    description="Multi-scenario AI-powered customer support assistant with real-time chat capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "BIWOCO AI Customer Support Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat"""
    from app.api.v1.websocket import websocket_endpoint as ws_handler
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        await ws_handler(websocket, conversation_id, db)
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return JSONResponse(
        content={"status": "healthy", "service": "chatbot-api"},
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )