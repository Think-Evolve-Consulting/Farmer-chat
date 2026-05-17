"""Conversation logging for farmer chat sessions."""
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


class ConversationLogger:
    """
    Logs chat interactions to plain text files, one file per session.

    Attributes:
        log_dir: Directory where log files are stored
        enabled: Whether logging is active
        session_id: Unique identifier for this session
        log_file: Open file handle for writing logs
        interaction_count: Number of logged interactions
        start_time: Session start timestamp
    """

    def __init__(self, log_dir: str, enabled: bool = True, model_name: str = "claude-sonnet-4-20250514"):
        """
        Initialize the conversation logger.

        Args:
            log_dir: Directory path for storing log files
            enabled: Whether logging is enabled
            model_name: The name of the LLM used for the session
        """
        self.log_dir = Path(log_dir)
        self.enabled = enabled
        self.model_name = model_name
        self.session_id: Optional[str] = None
        self.log_file: Optional[object] = None
        self.interaction_count: int = 0
        self.start_time: Optional[datetime] = None

        if self.enabled:
            self._create_session_file()

    def _create_session_id(self) -> str:
        """
        Generate a unique session ID.

        Returns:
            Session ID in format: session_YYYYMMDD_HHMMSS_{short_uuid}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{short_uuid}"

    def _create_session_file(self) -> None:
        """Create the log file and write session header."""
        try:
            # Create log directory if it doesn't exist
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Generate session ID and create log file
            self.session_id = self._create_session_id()
            self.start_time = datetime.now()

            log_file_path = self.log_dir / f"{self.session_id}.log"
            self.log_file = open(log_file_path, 'w', encoding='utf-8', errors='replace')

            # Write session header
            self._write_session_header()

        except (IOError, OSError) as e:
            print(f"Warning: Failed to create log file: {e}", file=sys.stderr)
            print("Logging disabled for this session", file=sys.stderr)
            self.enabled = False
            self.log_file = None

    def _write_session_header(self) -> None:
        """Write the session header to the log file."""
        header = f"""{'=' * 80}
FARMER CHAT SESSION LOG
{'=' * 80}
Session ID: {self.session_id}
Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Model: {self.model_name}
{'=' * 80}

"""
        self._safe_write(header)

    def log_interaction(
        self,
        query: str,
        response: str,
        context_results: list[dict]
    ) -> None:
        """
        Log a single chat interaction.

        Args:
            query: User's query text
            response: Assistant's response text
            context_results: Retrieved context chunks with metadata
        """
        if not self.enabled:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build interaction log entry
        log_entry = f"[{timestamp}]\n"
        log_entry += f"USER QUERY:\n{query}\n\n"

        # Add retrieved context
        log_entry += self._format_context_chunks(context_results)

        # Add assistant response
        log_entry += f"ASSISTANT RESPONSE:\n{response}\n\n"
        log_entry += f"{'=' * 80}\n\n"

        self._safe_write(log_entry)
        self.interaction_count += 1

    def _format_context_chunks(self, chunks: list[dict]) -> str:
        """
        Format retrieved context chunks for logging.

        Args:
            chunks: List of chunk dictionaries with text, metadata, and scores

        Returns:
            Formatted context string
        """
        if not chunks:
            return "RETRIEVED CONTEXT:\nNo relevant context found.\n\n"

        context = f"RETRIEVED CONTEXT ({len(chunks)} chunks):\n"

        for i, chunk in enumerate(chunks, 1):
            # Extract chunk data
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            similarity_score = chunk.get('similarity_score', 0.0)

            # Get source file (try both locations)
            source = chunk.get('source_file', metadata.get('file_name', 'Unknown'))
            chunk_index = chunk.get('chunk_index', 'Unknown')

            # Format chunk header with more debug info
            context += f"--- Chunk {i} (Relevance: {similarity_score:.2f}) ---\n"
            context += f"Source: {source}\n"
            context += f"Chunk Index: {chunk_index}\n"

            # Add metadata debug info
            if metadata:
                context += f"Metadata: "
                meta_items = []
                for key, value in metadata.items():
                    if key not in ['file_name']:  # Skip redundant fields
                        # Truncate long values
                        value_str = str(value)
                        if len(value_str) > 50:
                            value_str = value_str[:47] + "..."
                        meta_items.append(f"{key}={value_str}")
                context += ", ".join(meta_items) + "\n"

            # Format text content
            if text:
                # Truncate very long text for readability
                if len(text) > 800:
                    text_display = text[:800] + "\n... [truncated, full length: {} chars]".format(len(text))
                else:
                    text_display = text
                context += f"Text:\n{text_display}\n"
            else:
                context += "Text: [EMPTY]\n"

            context += "\n"

        return context

    def close(self) -> None:
        """Close the log file and write session footer."""
        if not self.enabled or not self.log_file:
            return

        try:
            # Calculate session duration
            duration = datetime.now() - self.start_time
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)

            # Write session footer
            footer = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
SESSION END
Total Interactions: {self.interaction_count}
Duration: {minutes}m {seconds}s
{'=' * 80}
"""
            self._safe_write(footer)

            # Close file
            self.log_file.close()
            self.log_file = None

        except (IOError, OSError) as e:
            print(f"Warning: Failed to close log file: {e}", file=sys.stderr)

    def _safe_write(self, content: str) -> None:
        """
        Write content to log file with error handling.

        Args:
            content: Text content to write
        """
        if not self.enabled or not self.log_file:
            return

        try:
            self.log_file.write(content)
            self.log_file.flush()  # Ensure immediate write
        except (IOError, OSError) as e:
            print(f"Warning: Failed to write to log: {e}", file=sys.stderr)
            self.enabled = False  # Disable for remainder of session

    def __del__(self):
        """Ensure log file is closed on object destruction."""
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass  # Suppress errors during cleanup
