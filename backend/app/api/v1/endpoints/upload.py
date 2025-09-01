"""
File upload endpoints for business context documents
"""

import os
import uuid
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.knowledge import KnowledgeBase
from app.services.knowledge_service import KnowledgeService
from app.services.document_parser import DocumentParser

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/context")
async def upload_business_context(
    file: UploadFile = File(...),
    scenario: str = Form(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and process business context document
    """
    # Validate file type
    file_ext = Path(file.filename or '').suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Save file temporarily
        file_id = str(uuid.uuid4())
        temp_file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
        
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        # Parse document content
        parser = DocumentParser()
        extracted_text = parser.parse_document(temp_file_path, file_ext)
        
        # Create knowledge base entries
        knowledge_service = KnowledgeService()
        
        # Chunk large documents
        chunks = parser.chunk_text(extracted_text, max_chunk_size=2000)
        
        created_entries = []
        for i, chunk in enumerate(chunks):
            # Create knowledge entry for each chunk
            knowledge_entry = knowledge_service.add_knowledge_entry(
                title=title or f"{file.filename} - Part {i+1}",
                content=chunk,
                category=f"{scenario.upper()}_BUSINESS_CONTEXT",
                tags=[scenario, "business_context", "uploaded"],
                source=file.filename,
                db=db
            )
            created_entries.append(knowledge_entry)
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully processed {file.filename}",
            "chunks_created": len(chunks),
            "total_characters": len(extracted_text),
            "knowledge_entries": [{"id": entry.id, "title": entry.title} for entry in created_entries]
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file_path.exists():
            os.remove(temp_file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/context/{scenario}")
async def get_business_context(
    scenario: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get uploaded business context for a scenario
    """
    knowledge_service = KnowledgeService()
    
    context_entries = knowledge_service.get_knowledge_by_category(
        category=f"{scenario.upper()}_BUSINESS_CONTEXT",
        db=db
    )
    
    return {
        "scenario": scenario,
        "context_entries": [
            {
                "id": entry.id,
                "title": entry.title,
                "content": entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
                "source": entry.source,
                "created_at": entry.created_at
            }
            for entry in context_entries
        ],
        "total_entries": len(context_entries)
    }


@router.delete("/context/{entry_id}")
async def delete_context_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a business context entry
    """
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == entry_id,
        KnowledgeBase.is_active == True
    ).first()
    
    if not knowledge:
        raise HTTPException(status_code=404, detail="Context entry not found")
    
    # Soft delete
    knowledge.is_active = False
    db.commit()
    
    return {"message": "Context entry deleted successfully"}


@router.post("/test-context")
async def test_context_search(
    query: str = Form(...),
    scenario: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Test context search for a query and scenario
    """
    knowledge_service = KnowledgeService()
    
    # Search in business context - return top 3 for better LLM context
    results = knowledge_service.semantic_search(
        query,
        limit=3,
        db=db,
        category=f"{scenario.upper()}_BUSINESS_CONTEXT"
    )
    
    return {
        "query": query,
        "scenario": scenario,
        "results": [
            {
                "title": result.title,
                "content": result.content[:300] + "..." if len(result.content) > 300 else result.content,
                "source": result.source
            }
            for result in results
        ]
    }