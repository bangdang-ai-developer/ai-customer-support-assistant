"""
Knowledge base schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class KnowledgeBaseBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    is_active: Optional[bool] = True


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(KnowledgeBaseBase):
    title: Optional[str] = None
    content: Optional[str] = None


class KnowledgeBaseInDBBase(KnowledgeBaseBase):
    id: Optional[int] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeBase(KnowledgeBaseInDBBase):
    pass


class KnowledgeBaseInDB(KnowledgeBaseInDBBase):
    pass