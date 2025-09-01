"""
Tests for conversation endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.conversation import Conversation
from app.core.security import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    # This is a simplified version - in a real test, you'd use proper authentication
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.username, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_conversation(test_user, auth_headers):
    """Test creating a new conversation"""
    conversation_data = {
        "title": "Test Conversation",
        "status": "active"
    }
    
    response = client.post(
        "/api/v1/conversations/",
        json=conversation_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert data["status"] == "active"
    assert data["user_id"] == test_user.id


def test_get_conversations(test_user, auth_headers):
    """Test retrieving conversations for a user"""
    # First create a conversation
    db = TestingSessionLocal()
    conversation = Conversation(
        title="Test Conversation",
        user_id=test_user.id,
        status="active"
    )
    db.add(conversation)
    db.commit()
    db.close()
    
    response = client.get("/api/v1/conversations/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test Conversation"


def test_get_conversation_by_id(test_user, auth_headers):
    """Test retrieving a specific conversation"""
    # Create a conversation
    db = TestingSessionLocal()
    conversation = Conversation(
        title="Test Conversation",
        user_id=test_user.id,
        status="active"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    conversation_id = conversation.id
    db.close()
    
    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert data["title"] == "Test Conversation"


def test_update_conversation(test_user, auth_headers):
    """Test updating a conversation"""
    # Create a conversation
    db = TestingSessionLocal()
    conversation = Conversation(
        title="Original Title",
        user_id=test_user.id,
        status="active"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    conversation_id = conversation.id
    db.close()
    
    update_data = {
        "title": "Updated Title",
        "status": "closed"
    }
    
    response = client.put(
        f"/api/v1/conversations/{conversation_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "closed"


def test_delete_conversation(test_user, auth_headers):
    """Test deleting a conversation"""
    # Create a conversation
    db = TestingSessionLocal()
    conversation = Conversation(
        title="To Be Deleted",
        user_id=test_user.id,
        status="active"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    conversation_id = conversation.id
    db.close()
    
    response = client.delete(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Conversation deleted successfully"
    
    # Verify it's deleted
    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert response.status_code == 404


def test_unauthorized_access():
    """Test that unauthorized requests are rejected"""
    response = client.get("/api/v1/conversations/")
    assert response.status_code == 401


# Cleanup
def teardown_module():
    """Clean up test database"""
    import os
    if os.path.exists("./test.db"):
        os.remove("./test.db")