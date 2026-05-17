# Kisan Chat - AI Agricultural Assistant

Kisan Chat is a full-stack multilingual assistant for farmers.
It combines a React + Vite frontend with a Python FastAPI backend that uses Anthropic Claude and FAISS-based retrieval (RAG).

## Project Structure

```text
.
|-- backend/
|   |-- data/
|   |-- requirements.txt
|   `-- src/
|       |-- api.py
|       `-- main.py
|-- frontend/
|   |-- public/
|   |-- src/
|   `-- package.json
|-- .gitignore
`-- README.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create backend env file:

```bash
cp .env.example .env
```

Required backend variable:

- `ANTHROPIC_API_KEY`

Start backend API:

```bash
python -m src.main --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:

- API root: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Optional: build FAISS index from transcript JSONL files:

```bash
python -m src.main --build data/transcripts
```

## Frontend Setup

```bash
cd frontend
npm install
```

Create frontend env file:

```bash
cp .env.example .env.local
```

Important frontend variables:

- `VITE_API_BASE_URL` (default `/api`)
- `VITE_BACKEND_URL` (default `http://localhost:8000`)
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Start frontend:

```bash
npm run dev
```

Default frontend URL: `http://localhost:5173`

## Tech Stack

- Frontend: React 18, Vite, Tailwind CSS, Supabase JS
- Backend: FastAPI, Uvicorn, Anthropic SDK, FAISS, sentence-transformers

## Notes On Large Files (No Git LFS)

This repository is configured to avoid committing large local artifacts.

- Large artifacts are ignored via `.gitignore` (for example `data/`, `models/`, `weights/`, `*.bin`, `*.pkl`).
- LFS tracking rules were removed from `.gitattributes`.

If a large file was already tracked earlier, untrack it once:

```bash
git rm --cached <path-to-file>
git commit -m "Stop tracking large artifact"
```
