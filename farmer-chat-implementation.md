# Farmer Chat Interface Implementation Guide

A retrieval-augmented generation (RAG) system that enables farmers to query historical chat transcripts using FAISS vector indexing and Anthropic's Claude API.

After each run, document all the changes that you have done in CHANGES.md 
Read the CHANGES.md file, to get the context of what all changes have been completed

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Implementation Steps](#implementation-steps)
6. [Testing Strategy](#testing-strategy)
7. [Running the Application](#running-the-application)

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  JSONL Files    │────▶│  Chunking &      │────▶│  FAISS Index    │
│  (Transcripts)  │     │  Embedding       │     │  (Vector Store) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Chat Interface │◀────│  Anthropic API   │◀────│  Context        │
│  (Response)     │     │  (Claude)        │     │  Retrieval      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          ▲
                                                          │
                        ┌──────────────────┐              │
                        │  User Query      │──────────────┘
                        └──────────────────┘
```

The system processes farmer chat transcripts through the following pipeline:

1. **Ingestion**: Parse JSONL files containing chat transcripts
2. **Chunking**: Split conversations into semantically meaningful chunks
3. **Embedding**: Generate vector embeddings using a sentence transformer model
4. **Indexing**: Store embeddings in a FAISS index for efficient similarity search
5. **Retrieval**: Find relevant chunks based on user queries
6. **Generation**: Send retrieved context to Claude for response generation

---

## Prerequisites

Ensure you have the following installed:

- Python 3.9 or higher
- pip (Python package manager)
- An Anthropic API key (obtain from [console.anthropic.com](https://console.anthropic.com))

---

## Project Structure

```
ralph-wigam/ (current directory)
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

---

## Installation

### Step 1: Create Project Directory
### Step 2: Create Virtual Environment
### Step 3: Install Dependencies
### Step 4: Configure Environment Variables


## Implementation Steps
### Step 1: Configuration Module
### Step 2: JSONL Parser and Chunker
### Step 3: Embedding Generator
### Step 4: FAISS Index Manager
### Step 5: Context Retriever
### Step 6: Anthropic Chat Client
### Step 7: Main Application Entry Point
---

## Testing Strategy

### Test Configuration
### Unit Tests
### Integration Tests
### Running Tests with Watch Mode
### Alternative: Using pytest-watch directly
### Pre-commit Hook for Tests

---

## Running the Application

### Step 1: Sample Data

Data is available under 
`./data/transcripts `

### Step 2: Build the Index

```bash
python -m src.main --build data/transcripts
```

### Step 3: Start Chat Interface

```bash
python -m src.main --chat
```

### Step 4: Run Tests 

```bash
./run_tests.sh
# Or directly:
ptw --runner "pytest --cov=src -v"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure you're in the project root and virtual env is activated |
| `FAISS index not found` | Run `--build` before `--chat` |
| `API key error` | Check `.env` file has valid `ANTHROPIC_API_KEY` |
| `Memory issues with large files` | Reduce `chunk_size` or process files in batches |
| `Slow embedding generation` | Use GPU if available: `pip install faiss-gpu` |

---

## Next Steps

1. **Web Interface**: Add a Flask/FastAPI frontend
2. **Streaming Responses**: Implement streaming for better UX
3. **Advanced Retrieval**: Add hybrid search (keyword + semantic)
4. **Feedback Loop**: Store user feedback to improve retrieval
5. **Multi-language Support**: Add translation for international farmers


---

## Verification Checklist

After implementation, verify:

- [ ] All tests pass: `pytest -v`
- [ ] Test watcher runs: `./run_tests.sh`
- [ ] UI launches: `streamlit run src/app.py`
- [ ] Index builds from sample data
- [ ] Chat returns relevant responses
- [ ] Context is displayed in UI

When you ahve completed all the above points, send a completion promise of "ALL DONE" 