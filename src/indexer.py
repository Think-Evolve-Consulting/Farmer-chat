"""FAISS index management for vector storage and retrieval."""
import json
import faiss
import numpy as np
from pathlib import Path
from typing import Optional

from .chunker import Chunk


class FAISSIndexer:
    """Manages FAISS index for chunk embeddings."""
    
    def __init__(self, dimension: int, index_path: Optional[str] = None):
        """
        Initialize the FAISS indexer.
        
        Args:
            dimension: Embedding dimension
            index_path: Path to save/load the index
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else None
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: list[dict] = []
    
    def create_index(self) -> None:
        """Create a new FAISS index using inner product similarity."""
        # Using IndexFlatIP for cosine similarity (after L2 normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
    
    def add_chunks(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """
        Add chunks and their embeddings to the index.
        
        Args:
            chunks: List of Chunk objects
            embeddings: Numpy array of embeddings
        """
        if self.index is None:
            self.create_index()
        
        # L2 normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store chunk metadata
        for chunk in chunks:
            self.chunks.append(chunk.to_dict())
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> list[tuple[dict, float]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (chunk_dict, similarity_score) tuples
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # L2 normalize query
        query_normalized = query_embedding.copy()
        faiss.normalize_L2(query_normalized)
        
        # Search
        scores, indices = self.index.search(query_normalized, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def save(self) -> None:
        """Save the index and metadata to disk."""
        if self.index is None or self.index_path is None:
            raise ValueError("Index or path not initialized")
        
        # Ensure directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save chunk metadata
        metadata_path = self.index_path.with_suffix(".meta.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "dimension": self.dimension,
                "chunks": self.chunks
            }, f, indent=2)
    
    def load(self) -> bool:
        """
        Load the index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if self.index_path is None:
            return False
        
        metadata_path = self.index_path.with_suffix(".meta.json")
        
        if not self.index_path.exists() or not metadata_path.exists():
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(str(self.index_path))
        
        # Load chunk metadata
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            self.chunks = metadata["chunks"]
            self.dimension = metadata["dimension"]
        
        return True
    
    @property
    def total_chunks(self) -> int:
        """Get the total number of indexed chunks."""
        return len(self.chunks) if self.chunks else 0