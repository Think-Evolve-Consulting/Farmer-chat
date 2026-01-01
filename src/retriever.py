
"""Context retrieval combining embedding and FAISS search."""
from pathlib import Path

from .chunker import TranscriptChunker, Chunk
from .embedder import EmbeddingGenerator
from .indexer import FAISSIndexer
from .config import config


class ContextRetriever:
    """Retrieves relevant context for user queries."""
    
    def __init__(
        self,
        embedder: EmbeddingGenerator = None,
        indexer: FAISSIndexer = None,
        chunker: TranscriptChunker = None
    ):
        """
        Initialize the context retriever.
        
        Args:
            embedder: Embedding generator instance
            indexer: FAISS indexer instance
            chunker: Transcript chunker instance
        """
        self.embedder = embedder or EmbeddingGenerator(config.embedding_model)
        self.indexer = indexer or FAISSIndexer(
            dimension=config.embedding_dimension,
            index_path=config.faiss_index_path
        )
        self.chunker = chunker or TranscriptChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
    
    def build_index(self, transcript_directory: str) -> int:
        """
        Build the FAISS index from JSONL transcripts.

        Args:
            transcript_directory: Path to directory containing JSONL files

        Returns:
            Number of chunks indexed
        """
        directory = Path(transcript_directory)

        # Collect all chunks
        print(f"\n=== STEP 1: Chunking Transcripts ===")
        chunks = list(self.chunker.process_directory(directory))

        if not chunks:
            print("No chunks found!")
            return 0

        print(f"\nTotal chunks collected: {len(chunks):,}")

        # Generate embeddings
        print(f"\n=== STEP 2: Generating Embeddings ===")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Create and populate index
        print(f"\n=== STEP 3: Building FAISS Index ===")
        self.indexer.create_index()
        self.indexer.add_chunks(chunks, embeddings)
        print(f"Added {len(chunks):,} chunks to FAISS index")

        # Save index
        print(f"\n=== STEP 4: Saving Index ===")
        self.indexer.save()
        print(f"Index saved to: {self.indexer.index_path}")

        return len(chunks)
    
    def load_index(self) -> bool:
        """
        Load existing FAISS index.
        
        Returns:
            True if loaded successfully
        """
        return self.indexer.load()
    
    def retrieve(self, query: str, top_k: int = None) -> list[dict]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query text
            top_k: Number of results to return
            
        Returns:
            List of chunk dictionaries with similarity scores
        """
        if top_k is None:
            top_k = config.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search index
        results = self.indexer.search(query_embedding, k=top_k)
        
        # Format results
        formatted_results = []
        for chunk_dict, score in results:
            formatted_results.append({
                **chunk_dict,
                "similarity_score": score
            })
        
        return formatted_results
    
    def format_context(self, results: list[dict]) -> str:
        """
        Format retrieved results into a context string.
        
        Args:
            results: List of retrieved chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"--- Relevant Conversation Excerpt {i} "
                f"(Relevance: {result['similarity_score']:.2f}) ---\n"
                f"Source: {result['metadata'].get('file_name', 'Unknown')}\n"
                f"{result['text']}"
            )
        
        return "\n\n".join(context_parts)