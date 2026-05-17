"""Tests for the chunker module."""
import pytest
from src.chunker import TranscriptChunker, Chunk


class TestTranscriptChunker:
    """Tests for TranscriptChunker class."""
    
    @pytest.mark.unit
    def test_parse_jsonl(self, chunker, sample_jsonl_file):
        """Test JSONL file parsing."""
        messages = chunker.parse_jsonl(sample_jsonl_file)
        
        assert len(messages) == 4
        assert messages[0]["speaker"] == "Farmer John"
        assert "wheat" in messages[0]["message"]
    
    @pytest.mark.unit
    def test_format_conversation(self, chunker, sample_messages):
        """Test conversation formatting."""
        formatted = chunker.format_conversation(sample_messages)
        
        assert "Farmer John" in formatted
        assert "Farmer Jane" in formatted
        assert "wheat crop" in formatted
        assert "[2024-01-15 09:00]" in formatted
    
    @pytest.mark.unit
    def test_chunk_text_basic(self, chunker):
        """Test basic text chunking."""
        text = "A" * 500
        chunks = chunker.chunk_text(text, "test.jsonl")
        
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.source_file == "test.jsonl" for c in chunks)
    
    @pytest.mark.unit
    def test_chunk_text_overlap(self):
        """Test chunk overlap functionality."""
        chunker = TranscriptChunker(chunk_size=100, chunk_overlap=20)
        text = "Word " * 100  # 500 characters
        chunks = chunker.chunk_text(text, "test.jsonl")
        
        # Verify overlap exists between consecutive chunks
        assert len(chunks) > 1
        for i in range(len(chunks) - 1):
            current_end = chunks[i].text[-20:]
            # Check some overlap exists
            assert chunks[i].chunk_index == i
    
    @pytest.mark.unit
    def test_chunk_metadata(self, chunker):
        """Test chunk metadata preservation."""
        text = "Test content for chunking"
        metadata = {"topic": "testing", "category": "unit_test"}
        
        chunks = chunker.chunk_text(text, "test.jsonl", base_metadata=metadata)
        
        assert len(chunks) == 1
        assert chunks[0].metadata["topic"] == "testing"
        assert chunks[0].metadata["category"] == "unit_test"
    
    @pytest.mark.unit
    def test_process_directory(self, chunker, sample_transcript_dir):
        """Test processing multiple JSONL files."""
        chunks = list(chunker.process_directory(sample_transcript_dir))
        
        assert len(chunks) > 0
        # Should have chunks from all 3 files
        source_files = set(c.source_file for c in chunks)
        assert len(source_files) == 3
    
    @pytest.mark.unit
    def test_empty_file_handling(self, chunker, tmp_path):
        """Test handling of empty JSONL files."""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.touch()
        
        messages = chunker.parse_jsonl(empty_file)
        assert messages == []