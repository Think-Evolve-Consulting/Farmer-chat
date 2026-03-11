# Kisan Chat

A bilingual (Hindi/English) AI chat assistant for farmers, powered by Azure OpenAI / Azure AI Foundry Agents.

## Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS
- **Backend:** FastAPI, Python 3.12, Azure AI Agents SDK
- **AI:** Azure OpenAI / Azure AI Foundry (streaming)

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [Python](https://www.python.org/) 3.10+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (for backend auth)
- An Azure OpenAI or Azure AI Foundry resource

---

## Setup

### 1. Clone the repo

```bash
git clone <repo-url>
cd Farmer-chat
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your Azure values:

| Variable | Description |
|---|---|
| `VITE_API_ENDPOINT` | Azure OpenAI chat completions path |
| `VITE_API_KEY` | Azure OpenAI API key |
| `VITE_API_BASE_URL` | Azure OpenAI base URL |
| `VITE_SEARCH_ENDPOINT` | *(Optional)* Azure AI Search endpoint for RAG |
| `VITE_SEARCH_INDEX` | *(Optional)* Azure AI Search index name |
| `VITE_SEARCH_KEY` | *(Optional)* Azure AI Search key |
| `VITE_BACKEND_URL` | Backend URL (default: `http://localhost:8000`) |

### 3. Install frontend dependencies

```bash
npm install
```

### 4. Set up Python backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Authenticate with Azure (for backend)

```bash
# Install Azure CLI first (Windows: winget install Microsoft.AzureCLI)
az login
```

---

## Running the App

### Start the backend

```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

### Start the frontend (in a separate terminal)

```bash
npm run dev
# Runs on http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Build for Production

```bash
npm run build
# Output in dist/
```
