"""Main application entry point for the farmer chat interface."""
import argparse
import sys
from pathlib import Path

from .chat_client import FarmerChatClient
from .retriever import ContextRetriever
from .conversation_logger import ConversationLogger
from .config import config


def build_index(transcript_dir: str) -> None:
    """Build the FAISS index from transcripts."""
    print(f"Building index from: {transcript_dir}")
    
    retriever = ContextRetriever()
    num_chunks = retriever.build_index(transcript_dir)
    
    print(f"Successfully indexed {num_chunks} chunks")
    print(f"Index saved to: {config.faiss_index_path}")


def interactive_chat() -> None:
    """Run interactive chat session."""
    print("Farmer Chat Interface")
    print("=" * 50)
    print("Type 'quit' to exit, 'clear' to reset conversation")
    print("=" * 50)

    # Validate config
    config.validate()

    # Initialize logger
    logger = None
    if config.conversation_logging_enabled:
        logger = ConversationLogger(log_dir=config.conversation_log_dir)

    # Initialize client with logger
    client = FarmerChatClient(logger=logger)

    # Load index
    if not client.retriever.load_index():
        print("Warning: No index found. Run with --build first.")
        print("Continuing without context retrieval...")
    else:
        print(f"Loaded index with {client.retriever.indexer.total_chunks} chunks")

    print()

    try:
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break

                if user_input.lower() == "clear":
                    client.clear_history()
                    print("Conversation cleared.")
                    continue

                # Get response
                response = client.chat(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    finally:
        # Close logger before exit
        if logger:
            logger.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Farmer Chat Interface")
    parser.add_argument(
        "--build",
        metavar="DIR",
        help="Build index from JSONL files in directory"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start interactive chat"
    )
    
    args = parser.parse_args()
    
    if args.build:
        build_index(args.build)
    elif args.chat:
        interactive_chat()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()