"""
Utility functions for working with embeddings
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pickle
import os


class EmbeddingUtils:
    """
    Utility class for embedding operations
    """

    @staticmethod
    def cosine_similarity_matrix(embeddings: List[List[float]]) -> np.ndarray:
        """
        Calculate cosine similarity matrix for a list of embeddings
        """
        if not embeddings:
            return np.array([])
        
        embeddings_array = np.array(embeddings)
        return cosine_similarity(embeddings_array)

    @staticmethod
    def find_most_similar(
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding
        Returns list of tuples (index, similarity_score)
        """
        if not candidate_embeddings:
            return []
        
        query_array = np.array(query_embedding).reshape(1, -1)
        candidates_array = np.array(candidate_embeddings)
        
        similarities = cosine_similarity(query_array, candidates_array)[0]
        
        # Get top-k most similar
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]

    @staticmethod
    def cluster_embeddings(
        embeddings: List[List[float]], 
        n_clusters: int = 5,
        random_state: int = 42
    ) -> Tuple[List[int], np.ndarray]:
        """
        Cluster embeddings using K-means
        Returns cluster labels and cluster centers
        """
        if not embeddings or len(embeddings) < n_clusters:
            return [], np.array([])
        
        embeddings_array = np.array(embeddings)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings_array)
        
        return cluster_labels.tolist(), kmeans.cluster_centers_

    @staticmethod
    def reduce_dimensionality(
        embeddings: List[List[float]], 
        n_components: int = 50
    ) -> np.ndarray:
        """
        Reduce dimensionality of embeddings using PCA
        """
        try:
            from sklearn.decomposition import PCA
        except ImportError:
            raise ImportError("scikit-learn is required for dimensionality reduction")
        
        if not embeddings:
            return np.array([])
        
        embeddings_array = np.array(embeddings)
        
        # Ensure n_components doesn't exceed available dimensions
        n_components = min(n_components, embeddings_array.shape[1], embeddings_array.shape[0])
        
        pca = PCA(n_components=n_components)
        reduced_embeddings = pca.fit_transform(embeddings_array)
        
        return reduced_embeddings

    @staticmethod
    def calculate_embedding_statistics(embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Calculate statistics for a collection of embeddings
        """
        if not embeddings:
            return {}
        
        embeddings_array = np.array(embeddings)
        
        return {
            "count": len(embeddings),
            "dimensions": embeddings_array.shape[1],
            "mean_norm": float(np.mean(np.linalg.norm(embeddings_array, axis=1))),
            "std_norm": float(np.std(np.linalg.norm(embeddings_array, axis=1))),
            "mean_values": embeddings_array.mean(axis=0).tolist(),
            "std_values": embeddings_array.std(axis=0).tolist()
        }

    @staticmethod
    def save_embeddings(
        embeddings: List[List[float]], 
        metadata: List[Dict[str, Any]], 
        filepath: str
    ) -> None:
        """
        Save embeddings and their metadata to a file
        """
        data = {
            "embeddings": embeddings,
            "metadata": metadata,
            "count": len(embeddings),
            "dimensions": len(embeddings[0]) if embeddings else 0
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def load_embeddings(filepath: str) -> Tuple[List[List[float]], List[Dict[str, Any]]]:
        """
        Load embeddings and metadata from a file
        """
        if not os.path.exists(filepath):
            return [], []
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        return data.get("embeddings", []), data.get("metadata", [])

    @staticmethod
    def normalize_embeddings(embeddings: List[List[float]]) -> List[List[float]]:
        """
        Normalize embeddings to unit length
        """
        if not embeddings:
            return []
        
        embeddings_array = np.array(embeddings)
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        
        normalized = embeddings_array / norms
        return normalized.tolist()

    @staticmethod
    def batch_similarity_search(
        query_embeddings: List[List[float]],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[List[Tuple[int, float]]]:
        """
        Perform similarity search for multiple queries at once
        """
        if not query_embeddings or not candidate_embeddings:
            return []
        
        query_array = np.array(query_embeddings)
        candidates_array = np.array(candidate_embeddings)
        
        # Calculate similarity matrix
        similarities = cosine_similarity(query_array, candidates_array)
        
        results = []
        for i, sim_row in enumerate(similarities):
            # Get top-k most similar for this query
            top_indices = np.argsort(sim_row)[-top_k:][::-1]
            query_results = [(int(idx), float(sim_row[idx])) for idx in top_indices]
            results.append(query_results)
        
        return results

    @staticmethod
    def embedding_diversity_score(embeddings: List[List[float]]) -> float:
        """
        Calculate a diversity score for a set of embeddings
        Higher score means more diverse embeddings
        """
        if len(embeddings) < 2:
            return 0.0
        
        # Calculate pairwise similarities
        sim_matrix = EmbeddingUtils.cosine_similarity_matrix(embeddings)
        
        # Get upper triangle (excluding diagonal)
        upper_triangle = sim_matrix[np.triu_indices_from(sim_matrix, k=1)]
        
        # Diversity is inverse of average similarity
        avg_similarity = np.mean(upper_triangle)
        diversity_score = 1.0 - avg_similarity
        
        return float(diversity_score)

    @staticmethod
    def find_outliers(
        embeddings: List[List[float]], 
        threshold: float = 2.0
    ) -> List[int]:
        """
        Find outlier embeddings using distance from centroid
        Returns indices of outlier embeddings
        """
        if not embeddings:
            return []
        
        embeddings_array = np.array(embeddings)
        centroid = np.mean(embeddings_array, axis=0)
        
        # Calculate distances from centroid
        distances = np.linalg.norm(embeddings_array - centroid, axis=1)
        
        # Find outliers using z-score
        mean_distance = np.mean(distances)
        std_distance = np.std(distances)
        
        if std_distance == 0:
            return []
        
        z_scores = (distances - mean_distance) / std_distance
        outlier_indices = np.where(np.abs(z_scores) > threshold)[0]
        
        return outlier_indices.tolist()

    @staticmethod
    def embedding_quality_check(embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Perform quality checks on embeddings
        """
        if not embeddings:
            return {"status": "empty", "issues": ["No embeddings provided"]}
        
        embeddings_array = np.array(embeddings)
        issues = []
        
        # Check for NaN or infinite values
        if np.isnan(embeddings_array).any():
            issues.append("Contains NaN values")
        
        if np.isinf(embeddings_array).any():
            issues.append("Contains infinite values")
        
        # Check for zero vectors
        norms = np.linalg.norm(embeddings_array, axis=1)
        zero_vectors = np.sum(norms == 0)
        if zero_vectors > 0:
            issues.append(f"Contains {zero_vectors} zero vectors")
        
        # Check dimensionality consistency
        dimensions = [len(emb) for emb in embeddings]
        if len(set(dimensions)) > 1:
            issues.append("Inconsistent embedding dimensions")
        
        # Check for duplicates
        unique_embeddings = np.unique(embeddings_array, axis=0)
        duplicates = len(embeddings) - len(unique_embeddings)
        if duplicates > 0:
            issues.append(f"Contains {duplicates} duplicate embeddings")
        
        status = "healthy" if not issues else "issues_found"
        
        return {
            "status": status,
            "issues": issues,
            "total_embeddings": len(embeddings),
            "unique_embeddings": len(unique_embeddings),
            "dimensions": embeddings_array.shape[1] if embeddings else 0
        }