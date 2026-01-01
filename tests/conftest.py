"""Pytest fixtures for farmer chat tests."""
import json
import pytest
import tempfile
import numpy as np
from pathlib import Path

from src.chunker import TranscriptChunker, Chunk
from src.embedder import EmbeddingGenerator
from src.indexer import FAISSIndexer
from src.retriever import ContextRetriever
from src.conversation_logger import ConversationLogger


@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {"speaker": "Farmer John", "message": "How's the wheat crop looking?", "timestamp": "2024-01-15 09:00"},
        {"speaker": "Farmer Jane", "message": "Pretty good! The rain last week helped.", "timestamp": "2024-01-15 09:05"},
        {"speaker": "Farmer John", "message": "Should I apply fertilizer now?", "timestamp": "2024-01-15 09:10"},
        {"speaker": "Farmer Jane", "message": "Wait until the soil dries a bit more.", "timestamp": "2024-01-15 09:15"},
    ]


@pytest.fixture
def sample_jsonl_file(sample_messages, tmp_path):
    """Create a temporary JSONL file with sample messages."""
    jsonl_path = tmp_path / "sample_chat.jsonl"
    with open(jsonl_path, "w") as f:
        for msg in sample_messages:
            f.write(json.dumps(msg) + "\n")
    return jsonl_path


@pytest.fixture
def sample_transcript_dir(sample_messages, tmp_path):
    """Create a temporary directory with sample JSONL files."""
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    
    # Create multiple JSONL files
    for i in range(3):
        jsonl_path = transcript_dir / f"chat_{i}.jsonl"
        with open(jsonl_path, "w") as f:
            for msg in sample_messages:
                modified_msg = {**msg, "speaker": f"{msg['speaker']}_{i}"}
                f.write(json.dumps(modified_msg) + "\n")
    
    return transcript_dir


@pytest.fixture
def chunker():
    """Create a TranscriptChunker instance."""
    return TranscriptChunker(chunk_size=200, chunk_overlap=20)


@pytest.fixture
def embedder():
    """Create an EmbeddingGenerator instance."""
    return EmbeddingGenerator(model_name="all-MiniLM-L6-v2")


@pytest.fixture
def indexer(tmp_path):
    """Create a FAISSIndexer instance."""
    index_path = tmp_path / "test_index.faiss"
    return FAISSIndexer(dimension=384, index_path=str(index_path))


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            text="Discussion about wheat fertilization timing",
            source_file="chat_1.jsonl",
            chunk_index=0,
            metadata={"topic": "fertilization"}
        ),
        Chunk(
            text="Best practices for irrigation in dry season",
            source_file="chat_2.jsonl",
            chunk_index=0,
            metadata={"topic": "irrigation"}
        ),
        Chunk(
            text="Pest control methods for corn crops",
            source_file="chat_3.jsonl",
            chunk_index=0,
            metadata={"topic": "pest_control"}
        ),
    ]


@pytest.fixture
def tmp_log_dir(tmp_path):
    """Temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def conversation_logger(tmp_log_dir):
    """ConversationLogger with temporary directory."""
    logger = ConversationLogger(log_dir=str(tmp_log_dir))
    yield logger
    logger.close()