"""Tests for the embedder module."""
import pytest
import numpy as np
from src.embedder import EmbeddingGenerator


class TestEmbeddingGenerator:
    """Tests for EmbeddingGenerator class."""
    
    @pytest.mark.unit
    def test_embed_text_returns_array(self, embedder):
        """Test single text embedding returns numpy array."""
        embedding = embedder.embed_text("Test farming question")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype == np.float32
    
    @pytest.mark.unit
    def test_embed_text_dimension(self, embedder):
        """Test embedding dimension matches model."""
        embedding = embedder.embed_text("Test text")
        
        assert len(embedding) == embedder.dimension
        assert embedder.dimension == 384  # all-MiniLM-L6-v2
    
    @pytest.mark.unit
    def test_embed_texts_batch(self, embedder):
        """Test batch embedding."""
        texts = [
            "How to fertilize wheat?",
            "Best irrigation practices",
            "Pest control methods"
        ]
        embeddings = embedder.embed_texts(texts)
        
        assert embeddings.shape == (3, 384)
        assert embeddings.dtype == np.float32
    
    @pytest.mark.unit
    def test_embed_query_shape(self, embedder):
        """Test query embedding has correct shape for FAISS."""
        query_embedding = embedder.embed_query("When to plant corn?")
        
        assert query_embedding.shape == (1, 384)
    
    @pytest.mark.unit
    def test_similar_texts_similar_embeddings(self, embedder):
        """Test that similar texts produce similar embeddings."""
        emb1 = embedder.embed_text("How to grow wheat")
        emb2 = embedder.embed_text("Growing wheat tips")
        emb3 = embedder.embed_text("Car repair manual")
        
        # Cosine similarity
        sim_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity
        assert sim_12 > sim_13
    
    @pytest.mark.unit
    def test_empty_text_handling(self, embedder):
        """Test handling of empty text."""
        embedding = embedder.embed_text("")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384