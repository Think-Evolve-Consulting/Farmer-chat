"""Tests for the indexer module."""
import pytest
import numpy as np
from src.indexer import FAISSIndexer
from src.chunker import Chunk


class TestFAISSIndexer:
    """Tests for FAISSIndexer class."""
    
    @pytest.mark.unit
    def test_create_index(self, indexer):
        """Test index creation."""
        indexer.create_index()
        
        assert indexer.index is not None
        assert indexer.index.ntotal == 0
    
    @pytest.mark.unit
    def test_add_chunks(self, indexer, sample_chunks):
        """Test adding chunks to index."""
        indexer.create_index()
        
        # Create dummy embeddings
        embeddings = np.random.rand(len(sample_chunks), 384).astype(np.float32)
        
        indexer.add_chunks(sample_chunks, embeddings)
        
        assert indexer.index.ntotal == len(sample_chunks)
        assert len(indexer.chunks) == len(sample_chunks)
    
    @pytest.mark.unit
    def test_search_returns_results(self, indexer, sample_chunks):
        """Test search functionality."""
        indexer.create_index()
        embeddings = np.random.rand(len(sample_chunks), 384).astype(np.float32)
        indexer.add_chunks(sample_chunks, embeddings)
        
        # Search with random query
        query = np.random.rand(1, 384).astype(np.float32)
        results = indexer.search(query, k=2)
        
        assert len(results) == 2
        assert all(isinstance(r, tuple) for r in results)
        assert all(isinstance(r[0], dict) for r in results)
        assert all(isinstance(r[1], float) for r in results)
    
    @pytest.mark.unit
    def test_search_empty_index(self, indexer):
        """Test search on empty index."""
        indexer.create_index()
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = indexer.search(query, k=5)
        
        assert results == []
    
    @pytest.mark.unit
    def test_save_and_load(self, indexer, sample_chunks):
        """Test index persistence."""
        indexer.create_index()
        embeddings = np.random.rand(len(sample_chunks), 384).astype(np.float32)
        indexer.add_chunks(sample_chunks, embeddings)
        
        # Save
        indexer.save()
        
        # Create new indexer and load
        new_indexer = FAISSIndexer(
            dimension=384,
            index_path=indexer.index_path
        )
        loaded = new_indexer.load()
        
        assert loaded is True
        assert new_indexer.index.ntotal == len(sample_chunks)
        assert len(new_indexer.chunks) == len(sample_chunks)
    
    @pytest.mark.unit
    def test_total_chunks_property(self, indexer, sample_chunks):
        """Test total_chunks property."""
        assert indexer.total_chunks == 0
        
        indexer.create_index()
        embeddings = np.random.rand(len(sample_chunks), 384).astype(np.float32)
        indexer.add_chunks(sample_chunks, embeddings)
        
        assert indexer.total_chunks == len(sample_chunks)