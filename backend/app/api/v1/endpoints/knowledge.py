"""
Knowledge base endpoints
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.core.dependencies import get_db, get_current_active_user
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("/", response_model=List[schemas.KnowledgeBase])
def read_knowledge_base(
    skip: int = 0,
    limit: int = 100,
    category: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve knowledge base entries
    """
    query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    if search:
        query = query.filter(
            KnowledgeBase.title.contains(search) |
            KnowledgeBase.content.contains(search)
        )
    
    knowledge_entries = query.offset(skip).limit(limit).all()
    return knowledge_entries


@router.post("/", response_model=schemas.KnowledgeBase)
def create_knowledge_base_entry(
    knowledge_in: schemas.KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new knowledge base entry
    """
    # Generate embeddings for the content
    knowledge_service = KnowledgeService()
    embedding = knowledge_service.generate_embedding(knowledge_in.content)
    
    knowledge = KnowledgeBase(
        **knowledge_in.dict(),
        embedding=embedding
    )
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge


@router.get("/{knowledge_id}", response_model=schemas.KnowledgeBase)
def read_knowledge_base_entry(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get knowledge base entry by ID
    """
    knowledge = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == knowledge_id,
            KnowledgeBase.is_active == True
        )
        .first()
    )
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")
    return knowledge


@router.put("/{knowledge_id}", response_model=schemas.KnowledgeBase)
def update_knowledge_base_entry(
    knowledge_id: int,
    knowledge_in: schemas.KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update knowledge base entry
    """
    knowledge = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == knowledge_id,
            KnowledgeBase.is_active == True
        )
        .first()
    )
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")
    
    update_data = knowledge_in.dict(exclude_unset=True)
    
    # Regenerate embeddings if content changed
    if "content" in update_data:
        knowledge_service = KnowledgeService()
        update_data["embedding"] = knowledge_service.generate_embedding(update_data["content"])
    
    for field, value in update_data.items():
        setattr(knowledge, field, value)
    
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge


@router.delete("/{knowledge_id}")
def delete_knowledge_base_entry(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete knowledge base entry (soft delete)
    """
    knowledge = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == knowledge_id,
            KnowledgeBase.is_active == True
        )
        .first()
    )
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge base entry not found")
    
    knowledge.is_active = False
    db.add(knowledge)
    db.commit()
    return {"message": "Knowledge base entry deleted successfully"}


@router.post("/search", response_model=List[schemas.KnowledgeBase])
def semantic_search(
    query: str,
    limit: int = Query(5, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Perform semantic search on knowledge base
    """
    knowledge_service = KnowledgeService()
    results = knowledge_service.semantic_search(query, limit=limit, db=db)
    return results