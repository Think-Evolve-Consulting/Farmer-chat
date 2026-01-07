"""Tests for conversation logger module."""
import pytest
import re
from pathlib import Path
from datetime import datetime

from src.conversation_logger import ConversationLogger


@pytest.mark.unit
def test_session_id_format(tmp_path):
    """Test that session ID follows expected format."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    # Session ID should match: session_YYYYMMDD_HHMMSS_{8-char-uuid}
    pattern = r"session_\d{8}_\d{6}_[a-f0-9]{8}"
    assert re.match(pattern, logger.session_id)

    logger.close()


@pytest.mark.unit
def test_session_header_creation(tmp_path):
    """Test that session header is written correctly."""
    logger = ConversationLogger(log_dir=str(tmp_path))
    logger.close()

    # Read log file
    log_files = list(tmp_path.glob("session_*.log"))
    assert len(log_files) == 1

    content = log_files[0].read_text(encoding='utf-8')

    # Check header elements
    assert "FARMER CHAT SESSION LOG" in content
    assert "Session ID:" in content
    assert "Start Time:" in content
    assert "Model: claude-sonnet-4-20250514" in content
    assert "=" * 80 in content


@pytest.mark.unit
def test_log_interaction_format(tmp_path):
    """Test that interaction logging formats correctly."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    query = "What is the best fertilizer for wheat?"
    response = "NPK fertilizer is commonly used for wheat crops."
    context_results = [
        {
            "text": "Wheat requires nitrogen-rich soil...",
            "source_file": "data/transcripts/kcc_data.jsonl",
            "chunk_index": 42,
            "metadata": {
                "file_name": "kcc_data.jsonl",
                "message_count": 100,
                "start_char": 0,
                "end_char": 500
            },
            "similarity_score": 0.87
        }
    ]

    logger.log_interaction(query, response, context_results)
    logger.close()

    # Read log file
    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check interaction elements
    assert "USER QUERY:" in content
    assert query in content
    assert "RETRIEVED CONTEXT (1 chunks):" in content
    assert "Chunk 1 (Relevance: 0.87)" in content
    assert "Source: data/transcripts/kcc_data.jsonl" in content or "Source: data\\transcripts\\kcc_data.jsonl" in content
    assert "Chunk Index: 42" in content
    assert "Metadata:" in content
    assert "Wheat requires nitrogen-rich soil..." in content
    assert "ASSISTANT RESPONSE:" in content
    assert response in content


@pytest.mark.unit
def test_context_chunk_formatting(tmp_path):
    """Test formatting of multiple context chunks."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    context_results = [
        {
            "text": "Chunk 1 text",
            "source_file": "file1.jsonl",
            "chunk_index": 0,
            "metadata": {"file_name": "file1.jsonl", "start_char": 0, "end_char": 100},
            "similarity_score": 0.92
        },
        {
            "text": "Chunk 2 text",
            "source_file": "file2.jsonl",
            "chunk_index": 5,
            "metadata": {"file_name": "file2.jsonl", "start_char": 500, "end_char": 600},
            "similarity_score": 0.85
        },
        {
            "text": "Chunk 3 text",
            "source_file": "file3.jsonl",
            "chunk_index": 10,
            "metadata": {"file_name": "file3.jsonl", "start_char": 1000, "end_char": 1100},
            "similarity_score": 0.78
        }
    ]

    logger.log_interaction("test query", "test response", context_results)
    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check all chunks are logged
    assert "RETRIEVED CONTEXT (3 chunks):" in content
    assert "Chunk 1 (Relevance: 0.92)" in content
    assert "Chunk 2 (Relevance: 0.85)" in content
    assert "Chunk 3 (Relevance: 0.78)" in content
    assert "file1.jsonl" in content
    assert "file2.jsonl" in content
    assert "file3.jsonl" in content
    assert "Chunk Index:" in content


@pytest.mark.unit
def test_no_context_handling(tmp_path):
    """Test logging when no context is retrieved."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    logger.log_interaction("test query", "test response", [])
    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    assert "RETRIEVED CONTEXT:" in content
    assert "No relevant context found." in content


@pytest.mark.unit
def test_session_footer(tmp_path):
    """Test that session footer is written with correct stats."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    # Log multiple interactions
    logger.log_interaction("query 1", "response 1", [])
    logger.log_interaction("query 2", "response 2", [])
    logger.log_interaction("query 3", "response 3", [])

    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check footer elements
    assert "SESSION END" in content
    assert "Total Interactions: 3" in content
    assert "Duration:" in content
    assert re.search(r"Duration: \d+m \d+s", content)


@pytest.mark.unit
def test_disabled_logger(tmp_path):
    """Test that disabled logger doesn't create files."""
    logger = ConversationLogger(log_dir=str(tmp_path), enabled=False)

    logger.log_interaction("query", "response", [])
    logger.close()

    # No log files should be created
    log_files = list(tmp_path.glob("session_*.log"))
    assert len(log_files) == 0


@pytest.mark.unit
def test_file_creation(tmp_path):
    """Test that log file is created in correct location."""
    log_dir = tmp_path / "logs" / "conversations"
    logger = ConversationLogger(log_dir=str(log_dir))
    logger.close()

    # Check directory was created
    assert log_dir.exists()
    assert log_dir.is_dir()

    # Check log file exists
    log_files = list(log_dir.glob("session_*.log"))
    assert len(log_files) == 1
    assert log_files[0].suffix == ".log"


@pytest.mark.unit
def test_multiple_interactions(tmp_path):
    """Test logging multiple sequential interactions."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    for i in range(5):
        logger.log_interaction(
            query=f"query {i}",
            response=f"response {i}",
            context_results=[]
        )

    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check all interactions are logged
    for i in range(5):
        assert f"query {i}" in content
        assert f"response {i}" in content

    # Check interaction count
    assert "Total Interactions: 5" in content


@pytest.mark.unit
def test_timestamps_present(tmp_path):
    """Test that all timestamps are present and formatted correctly."""
    logger = ConversationLogger(log_dir=str(tmp_path))
    logger.log_interaction("query", "response", [])
    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check timestamp format: YYYY-MM-DD HH:MM:SS
    timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

    # Should have timestamps for: start time, interaction, end time
    timestamps = re.findall(timestamp_pattern, content)
    assert len(timestamps) >= 3  # At least start, interaction, end


@pytest.mark.unit
def test_unicode_handling(tmp_path):
    """Test that unicode characters are handled correctly."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    # Test with unicode characters (Hindi text example)
    query = "सेब के पौधे की देखभाल कैसे करें?"
    response = "Apple plant care requires regular pruning and fertilization."
    context_results = [
        {
            "text": "सेब के पौधे पर 600 ग्राम पोटाश...",
            "metadata": {"file_name": "kcc_data_himachal.jsonl"},
            "similarity_score": 0.90
        }
    ]

    logger.log_interaction(query, response, context_results)
    logger.close()

    log_files = list(tmp_path.glob("session_*.log"))
    content = log_files[0].read_text(encoding='utf-8')

    # Check that unicode text is preserved
    assert query in content
    assert "सेब के पौधे पर 600 ग्राम पोटाश" in content


@pytest.mark.unit
def test_write_error_handling(tmp_path):
    """Test graceful degradation when write fails."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    # Close file handle to make it read-only (simulate write failure)
    logger.log_file.close()

    # Reopen as read-only to simulate permission error
    log_files = list(tmp_path.glob("session_*.log"))
    logger.log_file = open(log_files[0], 'r')

    # This should not raise an exception
    logger.log_interaction("query", "response", [])

    # Logger should be disabled after write error
    assert logger.enabled is False

    # Close the file
    logger.log_file.close()


@pytest.mark.integration
def test_full_session_workflow(tmp_path):
    """Test complete session workflow from start to finish."""
    logger = ConversationLogger(log_dir=str(tmp_path))

    # Simulate a conversation
    interactions = [
        ("What crops grow well in monsoon?", "Rice and maize are suitable.", [
            {
                "text": "Rice cultivation during monsoon...",
                "metadata": {"file_name": "farming_guide.jsonl"},
                "similarity_score": 0.88
            }
        ]),
        ("How to prevent pests?", "Use organic pesticides.", []),
        ("Best time to plant wheat?", "October to November.", [
            {
                "text": "Wheat planting season starts in October...",
                "metadata": {"file_name": "wheat_farming.jsonl"},
                "similarity_score": 0.92
            },
            {
                "text": "Temperature should be below 25°C...",
                "metadata": {"file_name": "wheat_farming.jsonl"},
                "similarity_score": 0.85
            }
        ])
    ]

    for query, response, context in interactions:
        logger.log_interaction(query, response, context)

    logger.close()

    # Verify log file
    log_files = list(tmp_path.glob("session_*.log"))
    assert len(log_files) == 1

    content = log_files[0].read_text(encoding='utf-8')

    # Verify structure
    assert content.startswith("=" * 80)
    assert "FARMER CHAT SESSION LOG" in content
    assert "Total Interactions: 3" in content

    # Verify all interactions
    assert "What crops grow well in monsoon?" in content
    assert "How to prevent pests?" in content
    assert "Best time to plant wheat?" in content
