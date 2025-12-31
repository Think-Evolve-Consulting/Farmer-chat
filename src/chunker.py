"""Chunking logic for chat transcripts."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Generator


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    
    text: str
    source_file: str
    chunk_index: int
    metadata: dict
    
    def to_dict(self) -> dict:
        """Convert chunk to dictionary."""
        return {
            "text": self.text,
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }


class TranscriptChunker:
    """Chunks chat transcripts from JSONL files."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def parse_jsonl(self, file_path: Path) -> list[dict]:
        """
        Parse a JSONL file containing chat transcripts.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            List of chat message dictionaries
        """
        messages = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))
        return messages
    
    def format_conversation(self, messages: list[dict]) -> str:
        """
        Format messages into a conversation string.
        
        Expected JSONL format:
        {"speaker": "Farmer John", "message": "How's the wheat crop?", "timestamp": "..."}
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted conversation string
        """
        formatted_lines = []
        for msg in messages:
            speaker = msg.get("speaker", "Unknown")
            message = msg.get("message", "")
            timestamp = msg.get("timestamp", "")
            
            if timestamp:
                formatted_lines.append(f"[{timestamp}] {speaker}: {message}")
            else:
                formatted_lines.append(f"{speaker}: {message}")
        
        return "\n".join(formatted_lines)
    
    def chunk_text(self, text: str, source_file: str, base_metadata: dict = None) -> list[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            source_file: Source file name for metadata
            base_metadata: Additional metadata to include
            
        Returns:
            List of Chunk objects
        """
        if base_metadata is None:
            base_metadata = {}
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Find chunk end
            end = start + self.chunk_size
            
            # Try to break at a natural boundary (newline or sentence end)
            if end < len(text):
                # Look for newline
                newline_pos = text.rfind("\n", start, end)
                if newline_pos > start + self.chunk_size // 2:
                    end = newline_pos + 1
                else:
                    # Look for sentence end
                    for delimiter in [". ", "! ", "? "]:
                        pos = text.rfind(delimiter, start, end)
                        if pos > start + self.chunk_size // 2:
                            end = pos + len(delimiter)
                            break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    source_file=source_file,
                    chunk_index=chunk_index,
                    metadata={
                        **base_metadata,
                        "start_char": start,
                        "end_char": end
                    }
                ))
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
    
    def process_directory(self, directory: Path) -> Generator[Chunk, None, None]:
        """
        Process all JSONL files in a directory.
        
        Args:
            directory: Path to directory containing JSONL files
            
        Yields:
            Chunk objects from all files
        """
        for jsonl_file in directory.glob("*.jsonl"):
            messages = self.parse_jsonl(jsonl_file)
            conversation_text = self.format_conversation(messages)
            
            metadata = {
                "file_name": jsonl_file.name,
                "message_count": len(messages)
            }
            
            yield from self.chunk_text(
                text=conversation_text,
                source_file=str(jsonl_file),
                base_metadata=metadata
            )