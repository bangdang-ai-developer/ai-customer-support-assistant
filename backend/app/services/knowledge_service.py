"""
Knowledge base service with simple local embeddings
"""

import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import KnowledgeBase


class SimpleEmbeddingService:
    """Simple local embedding service using basic text features"""
    
    def __init__(self):
        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate improved embedding using TF-IDF-like features"""
        try:
            # Clean and process text
            text = text.strip().lower()
            if not text:
                return [0.0] * 300
            
            # Extract features: words, bigrams, and character n-grams
            words = text.split()
            vocab_size = 300
            feature_vector = [0.0] * vocab_size
            
            # Add word features
            for word in words:
                if len(word) > 2:  # Skip very short words
                    feature_index = abs(hash(word)) % (vocab_size // 3)
                    feature_vector[feature_index] += 1.0
            
            # Add bigram features
            for i in range(len(words) - 1):
                bigram = f"{words[i]}_{words[i+1]}"
                feature_index = abs(hash(bigram)) % (vocab_size // 3) + (vocab_size // 3)
                feature_vector[feature_index] += 0.5
            
            # Add character 3-gram features
            clean_text = ''.join(words)
            for i in range(len(clean_text) - 2):
                trigram = clean_text[i:i+3]
                feature_index = abs(hash(trigram)) % (vocab_size // 3) + (2 * vocab_size // 3)
                feature_vector[feature_index] += 0.25
            
            # Normalize using L2 norm for better cosine similarity
            norm = sum(f * f for f in feature_vector) ** 0.5
            if norm > 0:
                feature_vector = [f / norm for f in feature_vector]
            
            return feature_vector
            
        except Exception as e:
            print(f"Error generating improved embedding: {str(e)}")
            return [0.0] * 300


class KnowledgeService:
    def __init__(self):
        self.embedding_service = SimpleEmbeddingService()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using simple local method"""
        return self.embedding_service.generate_embedding(text)

    def add_knowledge_entry(
        self, 
        title: str, 
        content: str, 
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        db: Session = None
    ) -> KnowledgeBase:
        """Add a new knowledge base entry with local embeddings"""
        
        # Generate embedding locally
        embedding = self.generate_embedding(f"{title} {content}")
        
        knowledge_entry = KnowledgeBase(
            title=title,
            content=content,
            category=category,
            tags=tags,
            source=source,
            embedding=embedding,
            is_active=True
        )
        
        if db:
            db.add(knowledge_entry)
            db.commit()
            db.refresh(knowledge_entry)
        
        return knowledge_entry

    def semantic_search(
        self, 
        query: str, 
        limit: int = 5, 
        db: Session = None,
        category: Optional[str] = None,
        min_similarity: float = 0.05
    ) -> List[KnowledgeBase]:
        """Perform semantic search using local embeddings"""
        
        if not db:
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Get all active knowledge entries
        query_obj = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
        
        if category:
            query_obj = query_obj.filter(KnowledgeBase.category == category)
        
        knowledge_entries = query_obj.all()
        
        if not knowledge_entries:
            return []
        
        # Calculate similarities
        similarities = []
        for entry in knowledge_entries:
            if entry.embedding:
                # Calculate cosine similarity
                similarity = self._calculate_similarity(
                    query_embedding, 
                    entry.embedding
                )
                similarities.append((entry, similarity))
        
        # Sort by similarity and filter by minimum threshold
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [
            entry for entry, sim in similarities 
            if sim >= min_similarity
        ][:limit]
        
        return results

    def update_knowledge_embedding(
        self, 
        knowledge_id: int, 
        db: Session
    ) -> bool:
        """Update embedding for a knowledge entry"""
        
        knowledge = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == knowledge_id)
            .first()
        )
        
        if not knowledge:
            return False
        
        # Generate new embedding locally
        new_embedding = self.generate_embedding(f"{knowledge.title} {knowledge.content}")
        knowledge.embedding = new_embedding
        
        db.add(knowledge)
        db.commit()
        
        return True

    def bulk_update_embeddings(self, db: Session) -> int:
        """Update embeddings for all knowledge entries"""
        
        entries_without_embeddings = (
            db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.is_active == True,
                KnowledgeBase.embedding.is_(None)
            )
            .all()
        )
        
        updated_count = 0
        for entry in entries_without_embeddings:
            try:
                embedding = self.generate_embedding(f"{entry.title} {entry.content}")
                entry.embedding = embedding
                db.add(entry)
                updated_count += 1
            except Exception as e:
                print(f"Error updating embedding for entry {entry.id}: {str(e)}")
        
        db.commit()
        return updated_count

    def get_related_entries(
        self, 
        knowledge_id: int, 
        limit: int = 5, 
        db: Session = None
    ) -> List[KnowledgeBase]:
        """Get entries related to a specific knowledge base entry"""
        
        if not db:
            return []
        
        source_entry = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.id == knowledge_id)
            .first()
        )
        
        if not source_entry or not source_entry.embedding:
            return []
        
        # Find similar entries
        return self.semantic_search(
            source_entry.content, 
            limit=limit + 1,  # +1 because we'll exclude the source entry
            db=db
        )[1:]  # Skip the first result (source entry itself)

    def get_knowledge_by_category(
        self, 
        category: str, 
        db: Session,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """Get knowledge entries by category"""
        
        return (
            db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.category == category,
                KnowledgeBase.is_active == True
            )
            .limit(limit)
            .all()
        )

    def search_by_tags(
        self, 
        tags: List[str], 
        db: Session,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """Search knowledge entries by tags"""
        
        results = []
        knowledge_entries = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.is_active == True)
            .all()
        )
        
        for entry in knowledge_entries:
            if entry.tags and any(tag in entry.tags for tag in tags):
                results.append(entry)
        
        return results[:limit]

    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0

    def get_knowledge_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        
        total_entries = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).count()
        entries_with_embeddings = (
            db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.is_active == True,
                KnowledgeBase.embedding.isnot(None)
            )
            .count()
        )
        
        # Get category distribution
        from sqlalchemy import func
        category_stats = (
            db.query(
                KnowledgeBase.category, 
                func.count(KnowledgeBase.id).label('count')
            )
            .filter(KnowledgeBase.is_active == True)
            .group_by(KnowledgeBase.category)
            .all()
        )
        
        return {
            "total_entries": total_entries,
            "entries_with_embeddings": entries_with_embeddings,
            "embedding_coverage": (entries_with_embeddings / total_entries * 100) if total_entries > 0 else 0,
            "categories": [{"name": cat, "count": count} for cat, count in category_stats],
            "embedding_type": "Simple local embeddings"
        }