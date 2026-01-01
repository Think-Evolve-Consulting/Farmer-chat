# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Retrieval-Augmented Generation (RAG) system** that enables farmers to query historical chat transcripts using FAISS vector indexing and Anthropic's Claude API. The system processes chat transcripts through chunking, embedding, and indexing, then provides an interactive chat interface that retrieves relevant context to answer farmer queries.


## Project Structure

```
farmer-chat/ (current directory)
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── chunker.py             # Text chunking logic
│   ├── embedder.py            # Embedding generation
│   ├── indexer.py             # FAISS index management
│   ├── retriever.py           # Context retrieval
│   ├── chat_client.py         # Anthropic API integration
│   └── main.py                # Application entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_indexer.py
│   ├── test_retriever.py
│   ├── test_chat_client.py
│   └── test_integration.py
├── data/
│   ├── transcripts/           # JSONL input files
│   └── index/                 # FAISS index storage
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with: ANTHROPIC_API_KEY=your_key_here
```

### Building the Index
```bash
# Build FAISS index from transcript files
python -m src.main --build data/transcripts
```

### Running the Chat Interface
```bash
# Start interactive chat (requires index to be built first)
python -m src.main --chat
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing -v

# Run with watch mode (auto-reruns on file changes)
./run_tests.sh
# Or directly: ptw --runner "pytest --cov=src -v"

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Step-by-Step: Creating FAISS Embeddings

This section provides a detailed walkthrough of building FAISS embeddings for the RAG system.

### Prerequisites
1. Python 3.8+ installed
2. Access to transcript data in JSONL format
3. Anthropic API key

### Step 1: Install Dependencies
```bash
# Install all required packages from requirements.txt
pip install -r requirements.txt
```

**Key packages installed:**
- `anthropic>=0.39.0` - Claude API client
- `faiss-cpu>=1.7.4` - FAISS vector similarity search
- `sentence-transformers>=2.2.2` - Embedding model
- `numpy>=1.24.0` - Numerical operations
- `python-dotenv>=1.0.0` - Environment variable management

### Step 2: Configure Environment
```bash
# Create .env file with required configuration
# Example .env contents:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
EMBEDDING_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_PATH=data/index/farmer_chat.index
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

**Configuration parameters:**
- `ANTHROPIC_API_KEY` - Your Claude API key (required)
- `EMBEDDING_MODEL` - Model for generating embeddings (384 dimensions)
- `FAISS_INDEX_PATH` - Where to save the index file
- `CHUNK_SIZE` - Characters per chunk (affects granularity)
- `CHUNK_OVERLAP` - Overlapping characters between chunks (preserves context)
- `TOP_K_RESULTS` - Number of relevant chunks to retrieve per query

### Step 3: Prepare Transcript Data
```bash
# Ensure transcript files are in JSONL format in data/transcripts/
# Each line should be a valid JSON object with conversation data
# Example structure:
# {"id": "conv_001", "messages": [...], "metadata": {...}}
```

**Expected data location:**
- `data/transcripts/*.jsonl` - All JSONL files in this directory will be processed

### Step 4: Build the FAISS Index
```bash
# Run the indexing command
python -m src.main --build data/transcripts
```

**What happens during indexing:**
1. **Loading**: Reads all JSONL files from `data/transcripts/`
2. **Chunking**: Splits conversations into 500-character chunks with 50-character overlap
3. **Embedding**: Generates 384-dimensional vectors using all-MiniLM-L6-v2 model
4. **Indexing**: Builds FAISS index for fast similarity search
5. **Persistence**: Saves index to `data/index/farmer_chat.index` and metadata to `farmer_chat.meta.json`

**Output files created:**
- `data/index/farmer_chat.index` - Binary FAISS index file
- `data/index/farmer_chat.meta.json` - Metadata (chunk count, dimension info)

**Example output:**
```
Building index from: data/transcripts
Successfully indexed 34170 chunks
Index saved to: data/index/farmer_chat.index
```

### Step 5: Verify Index Creation
```bash
# Check that index files exist
ls data/index/
# Should show: farmer_chat.index and farmer_chat.meta.json

# Verify index size (should contain thousands of chunks)
# Metadata file contains chunk count information
```

### Step 6: Test with Chat Interface
```bash
# Start the interactive chat to test retrieval
python -m src.main --chat
```

**Testing the index:**
- Ask questions related to your transcript content
- System retrieves top 5 most relevant chunks
- Claude uses retrieved context to generate responses

### Technical Details: Embedding Pipeline

**1. Text Chunking (chunker.py)**
```
Input: "Long conversation text..."
Process: Split into overlapping chunks
Output: ["chunk1 (500 chars)", "chunk2 (500 chars)", ...]
```

**2. Vector Embedding (embedder.py)**
```
Input: ["chunk1", "chunk2", ...]
Model: all-MiniLM-L6-v2 (sentence-transformers)
Output: numpy array of shape (n_chunks, 384)
```

**3. FAISS Indexing (indexer.py)**
```
Input: Embedding vectors (n_chunks × 384)
Index Type: FAISS IndexFlatL2 (L2 distance for similarity)
Output: Searchable index stored on disk
```

**4. Retrieval (retriever.py)**
```
Query: "What is crop rotation?"
Process:
  1. Embed query → 384-dim vector
  2. Search index for k=5 nearest neighbors
  3. Return top 5 most similar chunks
```

### Rebuilding the Index

**When to rebuild:**
- New transcript data added to `data/transcripts/`
- Configuration changes (CHUNK_SIZE, CHUNK_OVERLAP)
- Embedding model changes

**How to rebuild:**
```bash
# Simply re-run the build command
python -m src.main --build data/transcripts

# This will:
# 1. Process all transcripts (including new ones)
# 2. Overwrite existing index files
# 3. Update metadata
```

### Troubleshooting

**Issue: "ANTHROPIC_API_KEY not found"**
```bash
# Solution: Verify .env file exists and contains valid API key
cat .env | grep ANTHROPIC_API_KEY
```

**Issue: "No transcripts found"**
```bash
# Solution: Ensure JSONL files exist in data/transcripts/
ls data/transcripts/*.jsonl
```

**Issue: "Index file not found" during chat**
```bash
# Solution: Build the index first
python -m src.main --build data/transcripts
```

**Issue: Poor retrieval quality**
- Try adjusting CHUNK_SIZE (smaller = more granular, larger = more context)
- Increase TOP_K_RESULTS to retrieve more chunks
- Verify transcript data quality and format

## Architecture

The system follows a modular pipeline architecture:

```
JSONL Transcripts → Chunking → Embedding → FAISS Index
                                               ↓
User Query → Context Retrieval → Claude API → Response
```

### Core Components

1. **config.py** - Centralized configuration using environment variables and dataclass
   - Manages API keys, model settings, chunk sizes, and file paths
   - All configuration should use the shared `config` singleton

2. **chunker.py** - Text chunking with overlap
   - Splits transcripts into semantically meaningful chunks
   - Configurable chunk size (default 500) and overlap (default 50)

3. **embedder.py** - Vector embedding generation
   - Uses sentence-transformers (default: all-MiniLM-L6-v2, 384 dimensions)
   - Generates dense vector representations for semantic search

4. **indexer.py** - FAISS index management
   - Stores and retrieves vector embeddings efficiently
   - Persists index to disk at `data/index/farmer_chat.index`

5. **retriever.py** - Context retrieval orchestrator
   - Coordinates chunking, embedding, and indexing
   - Retrieves top-k relevant chunks (default k=5) for queries

6. **chat_client.py** - Anthropic API integration
   - Manages conversation history
   - Constructs prompts with retrieved context
   - Uses claude-sonnet-4-20250514 model

7. **main.py** - CLI entry point
   - `--build DIR`: Build index from transcripts
   - `--chat`: Start interactive chat session

### Data Flow

- **Input**: JSONL files in `data/transcripts/`
- **Index Storage**: FAISS index saved to `data/index/`
- **Processing**: Each conversation is chunked, embedded, and indexed
- **Query Time**: User query → embedding → similarity search → context → Claude → response

## Important Workflows

### Change Documentation
**After each implementation run, document all changes in CHANGES.md**. Always read CHANGES.md at the start to understand previous modifications.

### Index Building Before Chat
The index must be built before running chat. If index is missing, chat will continue without context retrieval (degraded functionality).

### Configuration Validation
The `config.validate()` method checks for required ANTHROPIC_API_KEY. This is called on chat startup.

## Testing Strategy

- **Unit tests** (`@pytest.mark.unit`) - Test individual components in isolation
- **Integration tests** (`@pytest.mark.integration`) - Test component interactions
- **Slow tests** (`@pytest.mark.slow`) - Long-running tests
- **Fixtures** in `tests/conftest.py` - Shared test setup

Test configuration in `pytest.ini` uses auto asyncio mode and strict marker enforcement.

## Environment Variables

Required in `.env` file:
- `ANTHROPIC_API_KEY` - Required for Claude API access

Optional configuration:
- `EMBEDDING_MODEL` - Sentence transformer model (default: all-MiniLM-L6-v2)
- `FAISS_INDEX_PATH` - Index storage location (default: data/index/farmer_chat.index)
- `CHUNK_SIZE` - Text chunk size (default: 500)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 50)
- `TOP_K_RESULTS` - Number of chunks to retrieve (default: 5)

## Key Design Patterns

1. **Singleton Configuration** - Single `config` instance shared across modules
2. **Separation of Concerns** - Each module has a single, well-defined responsibility
3. **Pipeline Architecture** - Data flows through discrete processing stages
4. **Lazy Index Loading** - Index loaded on-demand in chat client
5. **Stateful Chat Client** - Maintains conversation history across interactions
