"""Tests for the chat client module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.chat_client import FarmerChatClient, SYSTEM_PROMPT


class TestFarmerChatClient:
    """Tests for FarmerChatClient class."""
    
    @pytest.mark.unit
    def test_initialization(self):
        """Test client initialization."""
        with patch("src.chat_client.Anthropic"):
            client = FarmerChatClient(api_key="test_key")
            
            assert client.conversation_history == []
            assert client.retriever is not None
    
    @pytest.mark.unit
    def test_clear_history(self):
        """Test clearing conversation history."""
        with patch("src.chat_client.Anthropic"):
            client = FarmerChatClient(api_key="test_key")
            client.conversation_history = [{"role": "user", "content": "test"}]
            
            client.clear_history()
            
            assert client.conversation_history == []
    
    @pytest.mark.unit
    def test_chat_adds_to_history(self, sample_transcript_dir, tmp_path):
        """Test that chat adds messages to history."""
        with patch("src.chat_client.Anthropic") as mock_anthropic:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Test response")]
            mock_anthropic.return_value.messages.create.return_value = mock_response
            
            client = FarmerChatClient(api_key="test_key")
            client.retriever.indexer.index_path = tmp_path / "test.index"
            client.retriever.build_index(str(sample_transcript_dir))
            
            response = client.chat("Test question")
            
            assert len(client.conversation_history) == 2
            assert client.conversation_history[0]["role"] == "user"
            assert client.conversation_history[1]["role"] == "assistant"
    
    @pytest.mark.unit
    def test_chat_includes_context(self, sample_transcript_dir, tmp_path):
        """Test that chat includes retrieved context."""
        with patch("src.chat_client.Anthropic") as mock_anthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Response")]
            mock_client = mock_anthropic.return_value
            mock_client.messages.create.return_value = mock_response
            
            client = FarmerChatClient(api_key="test_key")
            client.retriever.indexer.index_path = tmp_path / "test.index"
            client.retriever.build_index(str(sample_transcript_dir))
            
            client.chat("Tell me about wheat")
            
            # Check that context was included
            call_args = mock_client.messages.create.call_args
            messages = call_args.kwargs["messages"]
            assert "Relevant Context" in messages[0]["content"] or "User Question" in messages[0]["content"]
    
    @pytest.mark.unit
    def test_get_context_only(self, sample_transcript_dir, tmp_path):
        """Test getting context without generating response."""
        with patch("src.chat_client.Anthropic"):
            client = FarmerChatClient(api_key="test_key")
            client.retriever.indexer.index_path = tmp_path / "test.index"
            client.retriever.build_index(str(sample_transcript_dir))
            
            results = client.get_context_only("wheat fertilizer")
            
            assert isinstance(results, list)
            # History should not be modified
            assert client.conversation_history == []
    
    @pytest.mark.unit
    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert SYSTEM_PROMPT is not None
        assert "farmer" in SYSTEM_PROMPT.lower()
        assert "context" in SYSTEM_PROMPT.lower()