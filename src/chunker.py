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

        Supports two JSONL formats:
        1. Chat format: {"speaker": "Farmer John", "message": "How's the wheat crop?", "timestamp": "..."}
        2. KCC format: {"QueryText": "...", "KccAns": "...", "Crop": "...", "QueryType": "...", ...}

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted conversation string
        """
        formatted_lines = []
        for msg in messages:
            # Check if this is KCC data format (has QueryText/KccAns)
            if "QueryText" in msg or "KccAns" in msg:
                # Format KCC data with relevant fields
                parts = []

                # Add timestamp if available
                if "CreatedOn" in msg:
                    parts.append(f"[{msg['CreatedOn']}]")

                # Add location info if available
                location_parts = []
                for field in ["StateName", "DistrictName", "BlockName"]:
                    if field in msg and msg[field]:
                        location_parts.append(msg[field])
                if location_parts:
                    parts.append(f"Location: {', '.join(location_parts)}")

                # Add crop/sector info
                if "Crop" in msg and msg["Crop"]:
                    parts.append(f"Crop: {msg['Crop']}")
                if "QueryType" in msg and msg["QueryType"]:
                    parts.append(f"QueryType: {msg['QueryType'].strip()}")

                # Add the Q&A
                if "QueryText" in msg and msg["QueryText"]:
                    query_text = msg["QueryText"].strip()
                    parts.append(f"Query: {query_text}")

                if "KccAns" in msg and msg["KccAns"]:
                    answer_text = msg["KccAns"].strip()
                    parts.append(f"Answer: {answer_text}")

                formatted_lines.append("\n".join(parts))
            else:
                # Original chat format
                speaker = msg.get("speaker", "Unknown")
                message = msg.get("message", "")
                timestamp = msg.get("timestamp", "")

                if timestamp:
                    formatted_lines.append(f"[{timestamp}] {speaker}: {message}")
                else:
                    formatted_lines.append(f"{speaker}: {message}")

        return "\n\n".join(formatted_lines)
    
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
    
    def process_directory(self, directory: Path, batch_size: int = 1000) -> Generator[Chunk, None, None]:
        """
        Process all JSONL files in a directory.

        Args:
            directory: Path to directory containing JSONL files
            batch_size: Number of messages to process at once (for memory efficiency)

        Yields:
            Chunk objects from all files
        """
        for jsonl_file in directory.glob("*.jsonl"):
            print(f"Processing {jsonl_file.name}...")
            total_messages = 0
            batch = []

            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            batch.append(json.loads(line))
                            total_messages += 1

                            # Process batch when it reaches batch_size
                            if len(batch) >= batch_size:
                                conversation_text = self.format_conversation(batch)

                                metadata = {
                                    "file_name": jsonl_file.name,
                                    "message_count": len(batch),
                                    "batch_start_line": line_num - len(batch) + 1,
                                    "batch_end_line": line_num
                                }

                                yield from self.chunk_text(
                                    text=conversation_text,
                                    source_file=str(jsonl_file),
                                    base_metadata=metadata
                                )

                                batch = []  # Clear batch

                                # Progress indicator
                                if total_messages % 10000 == 0:
                                    print(f"  Processed {total_messages:,} messages from {jsonl_file.name}")

                        except json.JSONDecodeError as e:
                            print(f"  Warning: Skipping invalid JSON at line {line_num}: {e}")
                            continue

                # Process remaining messages in the last batch
                if batch:
                    conversation_text = self.format_conversation(batch)

                    metadata = {
                        "file_name": jsonl_file.name,
                        "message_count": len(batch),
                        "batch_start_line": total_messages - len(batch) + 1,
                        "batch_end_line": total_messages
                    }

                    yield from self.chunk_text(
                        text=conversation_text,
                        source_file=str(jsonl_file),
                        base_metadata=metadata
                    )

            print(f"  Completed {jsonl_file.name}: {total_messages:,} total messages")