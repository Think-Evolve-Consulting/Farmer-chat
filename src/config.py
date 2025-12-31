"""Configuration management for the farmer chat application."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration settings."""
    
    # API settings
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Embedding settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # FAISS settings
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "data/index/farmer_chat.index")
    
    # Chunking settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Retrieval settings
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Claude model
    claude_model: str = "claude-sonnet-4-20250514"
    
    def validate(self) -> None:
        """Validate required configuration."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")


config = Config()