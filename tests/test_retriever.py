"""Tests for the retriever module."""
import pytest
from src.retriever import ContextRetriever


class TestContextRetriever:
    """Tests for ContextRetriever class."""
    
    @pytest.mark.unit
    def test_build_index(self, sample_transcript_dir, tmp_path):
        """Test building index from transcripts."""
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        
        num_chunks = retriever.build_index(str(sample_transcript_dir))
        
        assert num_chunks > 0
        assert retriever.indexer.total_chunks == num_chunks
    
    @pytest.mark.unit
    def test_retrieve(self, sample_transcript_dir, tmp_path):
        """Test context retrieval."""
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        retriever.build_index(str(sample_transcript_dir))
        
        results = retriever.retrieve("wheat fertilizer", top_k=3)
        
        assert len(results) <= 3
        assert all("text" in r for r in results)
        assert all("similarity_score" in r for r in results)
    
    @pytest.mark.unit
    def test_format_context(self, sample_transcript_dir, tmp_path):
        """Test context formatting."""
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        retriever.build_index(str(sample_transcript_dir))
        
        results = retriever.retrieve("farming question", top_k=2)
        formatted = retriever.format_context(results)
        
        assert isinstance(formatted, str)
        assert "Relevant Conversation Excerpt" in formatted or "No relevant context" in formatted
    
    @pytest.mark.unit
    def test_format_context_empty(self):
        """Test context formatting with no results."""
        retriever = ContextRetriever()
        
        formatted = retriever.format_context([])
        
        assert formatted == "No relevant context found."
    
    @pytest.mark.unit
    def test_load_index(self, sample_transcript_dir, tmp_path):
        """Test loading saved index."""
        index_path = tmp_path / "test.index"
        
        # Build and save
        retriever1 = ContextRetriever()
        retriever1.indexer.index_path = index_path
        retriever1.build_index(str(sample_transcript_dir))
        
        # Load in new retriever
        retriever2 = ContextRetriever()
        retriever2.indexer.index_path = index_path
        loaded = retriever2.load_index()
        
        assert loaded is True
        assert retriever2.indexer.total_chunks > 0