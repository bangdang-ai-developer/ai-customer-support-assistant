"""
FAISS-based local embedding service for vector database operations
"""

import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle
import json
from sentence_transformers import SentenceTransformer


class FAISSEmbeddingService:
    """Local embedding service using FAISS and SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a lightweight, fast embedding model
        all-MiniLM-L6-v2: 384 dimensions, good quality, fast inference
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # FAISS index for similarity search
        self.index = None
        self.id_to_metadata = {}  # Map FAISS index IDs to knowledge entry metadata
        self.next_id = 0
        
        # Storage paths
        self.storage_dir = Path("/app/faiss_storage")
        self.storage_dir.mkdir(exist_ok=True)
        self.index_path = self.storage_dir / "knowledge.index"
        self.metadata_path = self.storage_dir / "metadata.json"
        
        # Load existing index if available
        self._load_index()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using local SentenceTransformer model"""
        try:
            # Clean and preprocess text
            text = text.strip()
            if not text:
                return [0.0] * self.embedding_dim
            
            # Generate embedding
            embedding = self.model.encode([text], show_progress_bar=False)[0]
            return embedding.tolist()
            
        except Exception as e:
            print(f"Error generating local embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dim
    
    def add_to_index(
        self, 
        text: str, 
        knowledge_id: int,
        title: str,
        category: Optional[str] = None
    ) -> int:
        """Add text embedding to FAISS index"""
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        embedding_array = np.array([embedding], dtype=np.float32)
        
        # Initialize index if not exists
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product for cosine similarity
        
        # Add to index
        faiss_id = self.next_id
        self.index.add(embedding_array)
        
        # Store metadata
        self.id_to_metadata[faiss_id] = {
            "knowledge_id": knowledge_id,
            "title": title,
            "category": category,
            "text": text[:500] + "..." if len(text) > 500 else text  # Store truncated text for preview
        }
        
        self.next_id += 1
        
        # Save index and metadata
        self._save_index()
        
        return faiss_id
    
    def search_similar(
        self, 
        query: str, 
        limit: int = 5,
        category: Optional[str] = None,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for similar texts using FAISS"""
        
        if self.index is None or self.index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_array)
            
            # Search
            search_limit = min(limit * 2, self.index.ntotal)  # Search more, filter later
            scores, indices = self.index.search(query_array, search_limit)
            
            # Process results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for missing results
                    continue
                
                metadata = self.id_to_metadata.get(idx, {})
                
                # Filter by category if specified
                if category and metadata.get("category") != category:
                    continue
                
                # Filter by minimum score
                if score < min_score:
                    continue
                
                results.append({
                    "knowledge_id": metadata.get("knowledge_id"),
                    "title": metadata.get("title", "Unknown"),
                    "text": metadata.get("text", ""),
                    "category": metadata.get("category"),
                    "similarity_score": float(score)
                })
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            print(f"Error in FAISS search: {str(e)}")
            return []
    
    def remove_from_index(self, knowledge_id: int):
        """Remove entries for a specific knowledge ID"""
        # Note: FAISS doesn't support efficient deletion
        # In production, you might want to rebuild the index periodically
        # or use a more sophisticated indexing strategy
        pass
    
    def rebuild_index(self, knowledge_entries: List[Dict[str, Any]]):
        """Rebuild the entire FAISS index from knowledge entries"""
        
        # Create new index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.id_to_metadata = {}
        self.next_id = 0
        
        # Add all entries
        embeddings = []
        for entry in knowledge_entries:
            embedding = self.generate_embedding(entry["content"])
            embeddings.append(embedding)
            
            # Store metadata
            self.id_to_metadata[self.next_id] = {
                "knowledge_id": entry["id"],
                "title": entry["title"],
                "category": entry.get("category"),
                "text": entry["content"][:500] + "..." if len(entry["content"]) > 500 else entry["content"]
            }
            
            self.next_id += 1
        
        # Add all embeddings to index at once
        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
            self.index.add(embeddings_array)
        
        # Save index
        self._save_index()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS index"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_dim,
            "model_name": self.model_name,
            "storage_size_mb": self._get_storage_size(),
            "categories": list(set(
                metadata.get("category") 
                for metadata in self.id_to_metadata.values() 
                if metadata.get("category")
            ))
        }
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.index:
                faiss.write_index(self.index, str(self.index_path))
            
            with open(self.metadata_path, 'w') as f:
                json.dump({
                    "id_to_metadata": self.id_to_metadata,
                    "next_id": self.next_id
                }, f, indent=2)
                
        except Exception as e:
            print(f"Error saving FAISS index: {str(e)}")
    
    def _load_index(self):
        """Load FAISS index and metadata from disk"""
        try:
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    data = json.load(f)
                    self.id_to_metadata = {int(k): v for k, v in data.get("id_to_metadata", {}).items()}
                    self.next_id = data.get("next_id", 0)
                    
        except Exception as e:
            print(f"Error loading FAISS index: {str(e)}")
            # Initialize empty index
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.id_to_metadata = {}
            self.next_id = 0
    
    def _get_storage_size(self) -> float:
        """Get storage size in MB"""
        try:
            total_size = 0
            if self.index_path.exists():
                total_size += self.index_path.stat().st_size
            if self.metadata_path.exists():
                total_size += self.metadata_path.stat().st_size
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0