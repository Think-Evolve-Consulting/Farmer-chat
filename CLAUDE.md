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
│   ├── chunker.py             # Text chunking logic (supports KCC JSONL format)
│   ├── embedder.py            # Embedding generation
│   ├── indexer.py             # FAISS index management
│   ├── retriever.py           # Context retrieval
│   ├── chat_client.py         # Anthropic API integration
│   ├── conversation_logger.py # Conversation logging with timestamps
│   ├── api.py                 # FastAPI REST API backend
│   └── main.py                # Application entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_indexer.py
│   ├── test_retriever.py
│   ├── test_chat_client.py
│   ├── test_conversation_logger.py
│   └── test_integration.py
├── data/
│   ├── transcripts/           # JSONL input files (KCC format supported)
│   ├── index/                 # FAISS index storage
│   └── logs/
│       └── conversations/     # Conversation logs (session-based)
├── frontend/                  # TypeScript React chat interface
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
- `CONVERSATION_LOGGING_ENABLED` - Enable/disable conversation logging (default: true)
- `CONVERSATION_LOG_DIR` - Directory for conversation logs (default: data/logs/conversations)

### Step 3: Prepare Transcript Data
```bash
# Ensure transcript files are in JSONL format in data/transcripts/
# Two formats are supported:
```

**Supported JSONL Formats:**

1. **Chat format** (original):
```json
{"speaker": "Farmer John", "message": "How's the wheat crop?", "timestamp": "2024-01-15"}
```

2. **KCC format** (farming Q&A):
```json
{
  "QueryText": "Information regarding dose of Sulphate of potash in Apple?",
  "KccAns": "सेब के पौधे पर 600 ग्राम सल्फेट ऑफ़ पोटाश...",
  "StateName": "HIMACHAL PRADESH",
  "DistrictName": "MANDI",
  "Crop": "Apple",
  "QueryType": "Cultural Practices",
  "CreatedOn": "2022-07-23T09:36:57.063"
}
```

**Expected data location:**
- `data/transcripts/*.jsonl` - All JSONL files in this directory will be processed

### Step 4: Build the FAISS Index
```bash
# Run the indexing command
python -m src.main --build data/transcripts
```

**What happens during indexing:**
1. **Loading**: Reads all JSONL files from `data/transcripts/` in batches (1,000 messages at a time)
2. **Chunking**: Splits conversations into 500-character chunks with 50-character overlap
3. **Embedding**: Generates 384-dimensional vectors using all-MiniLM-L6-v2 model (batch_size=128)
4. **Indexing**: Builds FAISS index for fast similarity search
5. **Persistence**: Saves index to `data/index/farmer_chat.index` and metadata to `farmer_chat.meta.json`

**Performance (Optimized in Jan 2026):**
- Processes large files (650k+ lines) in batches to maintain low memory usage (~20 MB)
- Progress indicators every 10,000 messages
- Expected time: 15-30 minutes for 1.5M records (previously 5+ hours)
- GPU acceleration: If PyTorch with CUDA is available, embedding generation is 10-50x faster

**Output files created:**
- `data/index/farmer_chat.index.v0` - Binary FAISS index file (52.5 MB)
- `data/index/farmer_chat.meta.json.v0` - Metadata with all chunks and their text (28.9 MB)

**Example output (with progress tracking):**
```
=== STEP 1: Chunking Transcripts ===
Processing kcc_data_apple.jsonl...
  Processed 10,000 messages from kcc_data_apple.jsonl
  Processed 20,000 messages from kcc_data_apple.jsonl
  ...
  Completed kcc_data_apple.jsonl: 308,448 total messages

Processing kcc_data_himachal.jsonl...
  Processed 10,000 messages from kcc_data_himachal.jsonl
  ...

Total chunks collected: 34,170

=== STEP 2: Generating Embeddings ===
Generating embeddings for 34,170 chunks (batch_size=128)...
[████████████████████] 100%

=== STEP 3: Building FAISS Index ===
Added 34,170 chunks to FAISS index

=== STEP 4: Saving Index ===
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

8. **conversation_logger.py** - Conversation logging (Added Jan 2026)
   - Logs all chat interactions with datetime stamps
   - Captures user queries, LLM responses, and retrieved context
   - Plain text format for human readability
   - One log file per session with unique session IDs
   - Fail-safe design (logging errors never break chat)
   - Configurable via environment variables

9. **api.py** - FastAPI REST API backend
   - Provides REST endpoints for chat functionality
   - Integrates with conversation logger
   - CORS support for frontend integration

### Data Flow

- **Input**: JSONL files in `data/transcripts/` (supports Chat and KCC formats)
- **Index Storage**: FAISS index saved to `data/index/`
- **Processing**: Each conversation is chunked, embedded, and indexed
- **Query Time**: User query → embedding → similarity search → context → Claude → response
- **Logging**: All interactions logged to `data/logs/conversations/session_*.log` (if enabled)

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
- `CONVERSATION_LOGGING_ENABLED` - Enable conversation logging (default: true)
- `CONVERSATION_LOG_DIR` - Directory for logs (default: data/logs/conversations)

## Key Design Patterns

1. **Singleton Configuration** - Single `config` instance shared across modules
2. **Separation of Concerns** - Each module has a single, well-defined responsibility
3. **Pipeline Architecture** - Data flows through discrete processing stages
4. **Lazy Index Loading** - Index loaded on-demand in chat client
5. **Stateful Chat Client** - Maintains conversation history across interactions
6. **Dependency Injection** - Logger injected into chat client for flexibility

## Conversation Logging (Added Jan 2026)

### Overview
The system automatically logs all chat interactions with detailed debugging information. Logs are stored in plain text format for easy human readability and debugging.

### Features
- ✅ Datetime stamps for every interaction
- ✅ Complete LLM responses (no truncation)
- ✅ Retrieved FAISS context chunks with relevance scores
- ✅ Session-based log files with unique IDs
- ✅ Fail-safe design (logging errors never break chat)
- ✅ Configurable via environment variables

### Log File Location
```
data/logs/conversations/session_YYYYMMDD_HHMMSS_{uuid}.log
```

**Example**: `session_20260101_143052_a4f8e4a3.log`

### Log Format

```
================================================================================
FARMER CHAT SESSION LOG
================================================================================
Session ID: session_20260101_143052_a4f8e4a3
Start Time: 2026-01-01 14:30:52
Model: claude-sonnet-4-20250514
================================================================================

[2026-01-01 14:31:15]
USER QUERY:
What is the best fertilizer for wheat?

RETRIEVED CONTEXT (5 chunks):
--- Chunk 1 (Relevance: 0.87) ---
Source: data/transcripts/kcc_data_apple.jsonl
Chunk Index: 42
Metadata: message_count=308448, start_char=0, end_char=500
Text:
[2022-07-23T09:36:57.063]
Location: HIMACHAL PRADESH, MANDI, KARSOG
Crop: Apple
QueryType: Cultural Practices
Query: Information regarding dose of Sulphate of potash in Apple?
Answer: सेब के पौधे पर 600 ग्राम सल्फेट ऑफ़ पोटाश...

--- Chunk 2 (Relevance: 0.82) ---
...

ASSISTANT RESPONSE:
Based on the historical conversations, wheat farming typically benefits...

================================================================================

[2026-01-01 14:32:03]
SESSION END
Total Interactions: 2
Duration: 0m 48s
================================================================================
```

### Configuration

**Enable/Disable Logging:**
```bash
# In .env file
CONVERSATION_LOGGING_ENABLED=true  # Set to false to disable
CONVERSATION_LOG_DIR=data/logs/conversations
```

**Programmatic Control:**
```python
from src.conversation_logger import ConversationLogger

# Create logger
logger = ConversationLogger(
    log_dir="data/logs/conversations",
    enabled=True
)

# Use with chat client
from src.chat_client import FarmerChatClient
client = FarmerChatClient(logger=logger)
```

### Use Cases

1. **Debugging Retrieval Quality**
   - See which chunks were retrieved and their relevance scores
   - Understand why certain context was selected
   - Identify gaps in the knowledge base

2. **Monitoring LLM Responses**
   - Review complete responses for quality
   - Track conversation flow
   - Analyze answer patterns

3. **Compliance & Auditing**
   - Maintain records of all interactions
   - Track usage patterns
   - Review historical queries

4. **Data Analysis**
   - Identify common farmer questions
   - Find areas needing more context
   - Improve retrieval strategy

### Log File Details

**Files are portable:**
- Can be copied between machines
- Plain text format (UTF-8 encoding)
- Human-readable, no special tools needed
- Grep-friendly for searching

**Session Management:**
- One file per session (CLI or API instance)
- Unique session IDs prevent collisions
- Chronologically sortable by timestamp

**Error Handling:**
- Logging failures never interrupt chat
- Graceful degradation on disk full/permissions
- Warnings printed to stderr
- Chat continues normally

## Performance Optimizations (Jan 2026)

### Index Building Performance

**Problem:** Building FAISS index was taking 5+ hours for 1.5M records

**Solution:** Implemented batch processing and optimized embedding generation

### Key Improvements

1. **Batch Processing for Large JSONL Files**
   - Process files in batches of 1,000 messages
   - Constant memory usage (~20 MB) regardless of file size
   - Prevents loading 650k+ lines into memory at once
   - **20-30x faster** chunking

2. **Increased Embedding Batch Size**
   - Changed from `batch_size=32` to `batch_size=128`
   - Better GPU/CPU utilization
   - **4x faster** embedding generation

3. **Progress Tracking**
   - Real-time progress indicators every 10,000 messages
   - Step-by-step phase reporting
   - Clear visibility into build progress

### Performance Results

| Phase | Before | After | Speedup |
|-------|--------|-------|---------|
| Chunking | 3-4 hours | 5-10 minutes | **20-30x** |
| Embedding | 1-2 hours | 10-20 minutes | **4x** |
| Indexing | <1 minute | <1 minute | Same |
| **Total** | **5+ hours** | **15-30 minutes** | **10-20x** |

### GPU Acceleration

**Embedding generation automatically uses GPU if available:**
- Requires PyTorch with CUDA
- No code changes needed
- 10-50x faster than CPU for embeddings
- Expected total time with GPU: ~6-12 minutes

**FAISS Index Compatibility:**
- Index built with GPU embeddings works on CPU-only machines
- Index files are device-independent
- No `faiss-gpu` required for inference
- Portable across platforms (Windows ↔ Linux ↔ Mac)

### Memory Usage

**Before:** 2-3 GB RAM per large file (OOM errors possible)

**After:** Constant ~20 MB RAM (independent of file size)

## KCC Data Format Support (Jan 2026)

### Overview
The chunker now supports the KCC (Kisan Call Center) JSONL format used for farming Q&A data.

### Supported Fields

The system extracts and formats these KCC fields:
- `QueryText` - Farmer's question
- `KccAns` - Expert's answer
- `StateName`, `DistrictName`, `BlockName` - Location information
- `Crop` - Crop type (Apple, Wheat, etc.)
- `QueryType` - Category (Cultural Practices, Plant Protection, etc.)
- `CreatedOn` - Timestamp
- `Sector`, `Category`, `Season` - Additional metadata

### Formatted Output

**Before (with old chunker):**
```
Unknown:
Unknown:
Unknown:
```

**After (with KCC format support):**
```
[2022-07-23T09:36:57.063]
Location: HIMACHAL PRADESH, MANDI, KARSOG
Crop: Apple
QueryType: Cultural Practices
Query: Information regarding dose of Sulphate of potash in Apple?
Answer: सेब के पौधे पर 600 ग्राम सल्फेट ऑफ़ पोटाश (NPK 00:00:50) को 200 लीटर पानी में मिला कर तुड़ाई से 30 दिन पहले छिड़काव करे|
```

### Benefits

1. **Better Context** - Location and crop info helps LLM provide region-specific advice
2. **Preserved Language** - Hindi/English text maintained correctly
3. **Structured Q&A** - Clear query/answer separation
4. **Rich Metadata** - Query type helps with categorization
5. **Debugging** - Easy to understand what content was retrieved

### Backward Compatibility

The chunker still supports the original chat format:
```json
{"speaker": "Farmer John", "message": "How's the wheat crop?", "timestamp": "2024-01-15"}
```

Both formats can coexist in the same `data/transcripts/` directory.
