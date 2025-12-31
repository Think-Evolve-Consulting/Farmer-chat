"""Integration tests for the complete pipeline."""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.chunker import TranscriptChunker
from src.embedder import EmbeddingGenerator
from src.indexer import FAISSIndexer
from src.retriever import ContextRetriever
from src.chat_client import FarmerChatClient


class TestPipelineIntegration:
    """Integration tests for the complete RAG pipeline."""
    
    @pytest.mark.integration
    def test_full_indexing_pipeline(self, sample_transcript_dir, tmp_path):
        """Test complete indexing pipeline."""
        # Initialize components
        chunker = TranscriptChunker(chunk_size=200, chunk_overlap=20)
        embedder = EmbeddingGenerator()
        indexer = FAISSIndexer(dimension=384, index_path=str(tmp_path / "test.index"))
        
        # Process transcripts
        chunks = list(chunker.process_directory(sample_transcript_dir))
        assert len(chunks) > 0
        
        # Generate embeddings
        texts = [c.text for c in chunks]
        embeddings = embedder.embed_texts(texts)
        assert embeddings.shape[0] == len(chunks)
        
        # Build index
        indexer.create_index()
        indexer.add_chunks(chunks, embeddings)
        indexer.save()
        
        # Verify persistence
        new_indexer = FAISSIndexer(dimension=384, index_path=str(tmp_path / "test.index"))
        assert new_indexer.load() is True
        assert new_indexer.total_chunks == len(chunks)
    
    @pytest.mark.integration
    def test_retrieval_relevance(self, sample_transcript_dir, tmp_path):
        """Test that retrieval returns relevant results."""
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        retriever.build_index(str(sample_transcript_dir))
        
        # Query about wheat (present in test data)
        results = retriever.retrieve("wheat crop fertilizer", top_k=3)
        
        # Should find relevant chunks
        assert len(results) > 0
        combined_text = " ".join(r["text"].lower() for r in results)
        # At least one result should mention wheat or fertilizer
        assert "wheat" in combined_text or "fertilizer" in combined_text
    
    @pytest.mark.integration
    def test_end_to_end_chat(self, sample_transcript_dir, tmp_path):
        """Test complete chat flow."""
        with patch("src.chat_client.Anthropic") as mock_anthropic:
            # Setup mock
            mock_response = MagicMock()
            mock_response.content = [MagicMock(
                text="Based on the farmer discussions, you should wait for the soil to dry before applying fertilizer."
            )]
            mock_anthropic.return_value.messages.create.return_value = mock_response
            
            # Initialize client
            client = FarmerChatClient(api_key="test_key")
            client.retriever.indexer.index_path = tmp_path / "test.index"
            client.retriever.build_index(str(sample_transcript_dir))
            
            # Chat
            response = client.chat("When should I fertilize my wheat?")
            
            assert isinstance(response, str)
            assert len(response) > 0
            
            # Verify API was called with context
            call_args = mock_anthropic.return_value.messages.create.call_args
            assert call_args.kwargs["model"] is not None
            assert len(call_args.kwargs["messages"]) > 0
    
    @pytest.mark.integration
    def test_multi_turn_conversation(self, sample_transcript_dir, tmp_path):
        """Test multi-turn conversation maintains context."""
        with patch("src.chat_client.Anthropic") as mock_anthropic:
            # Setup mock
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Response")]
            mock_anthropic.return_value.messages.create.return_value = mock_response
            
            client = FarmerChatClient(api_key="test_key")
            client.retriever.indexer.index_path = tmp_path / "test.index"
            client.retriever.build_index(str(sample_transcript_dir))
            
            # Multiple turns
            client.chat("Question 1")
            client.chat("Question 2")
            client.chat("Question 3")
            
            # History should have all turns
            assert len(client.conversation_history) == 6  # 3 user + 3 assistant
            
            # Clear and verify
            client.clear_history()
            assert len(client.conversation_history) == 0


class TestDataFormats:
    """Tests for various data format scenarios."""
    
    @pytest.mark.integration
    def test_large_transcript_handling(self, tmp_path):
        """Test handling of large transcripts."""
        # Create large JSONL file
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()
        
        large_file = transcript_dir / "large_chat.jsonl"
        with open(large_file, "w") as f:
            for i in range(1000):
                msg = {
                    "speaker": f"Farmer_{i % 10}",
                    "message": f"This is message number {i} about farming topics like wheat, corn, and irrigation." * 5,
                    "timestamp": f"2024-01-15 {i // 60:02d}:{i % 60:02d}"
                }
                f.write(json.dumps(msg) + "\n")
        
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        num_chunks = retriever.build_index(str(transcript_dir))
        
        # Should create multiple chunks
        assert num_chunks > 10
        
        # Should still retrieve quickly
        results = retriever.retrieve("irrigation tips", top_k=5)
        assert len(results) <= 5
    
    @pytest.mark.integration
    def test_missing_fields_handling(self, tmp_path):
        """Test handling of messages with missing fields."""
        transcript_dir = tmp_path / "transcripts"
        transcript_dir.mkdir()
        
        incomplete_file = transcript_dir / "incomplete.jsonl"
        with open(incomplete_file, "w") as f:
            # Various incomplete formats
            f.write(json.dumps({"speaker": "John", "message": "Hello"}) + "\n")
            f.write(json.dumps({"message": "No speaker"}) + "\n")
            f.write(json.dumps({"speaker": "Jane"}) + "\n")
            f.write(json.dumps({}) + "\n")
        
        retriever = ContextRetriever()
        retriever.indexer.index_path = tmp_path / "test.index"
        
        # Should not raise exception
        num_chunks = retriever.build_index(str(transcript_dir))
        assert num_chunks >= 0