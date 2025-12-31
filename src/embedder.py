"""Embedding generation using sentence transformers."""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Union


class EmbeddingGenerator:
    """Generates embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def embed_texts(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings.astype(np.float32)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.
        
        Args:
            query: Query text
            
        Returns:
            Numpy array of embedding vector, reshaped for FAISS
        """
        embedding = self.embed_text(query)
        return embedding.reshape(1, -1)