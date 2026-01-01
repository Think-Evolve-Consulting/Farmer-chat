# Quick Start Guide - Farmer Chat Application

This guide will help you start both the backend API and frontend chat interface.

## Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ and npm installed
- ✅ FAISS index already built (34,170 chunks)

---

## Step-by-Step Instructions

### Step 1: Open Two Terminal Windows

You'll need **two separate terminal/command prompt windows**:
- **Terminal 1** - For the Python backend
- **Terminal 2** - For the React frontend

---

### Step 2: Start the Backend API (Terminal 1)

#### 2.1 Navigate to Project Root
```bash
cd "F:\TTTR - eKutir Data\Farmer-chat"
```

#### 2.2 Install Backend Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

Wait for all packages to install. You should see:
- ✅ fastapi
- ✅ uvicorn
- ✅ anthropic
- ✅ faiss-cpu
- ✅ sentence-transformers

#### 2.3 Start the Backend Server
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**What you should see:**
```
INFO:     Will watch for changes in these directories: ['F:\\TTTR - eKutir Data\\Farmer-chat']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Important Messages:**
- You'll see: "Loaded index with 34170 chunks" - This means the FAISS index loaded successfully ✅
- If you see warnings about missing index, run: `python -m src.main --build data/transcripts`

**Keep this terminal window open!** The backend must stay running.

---

### Step 3: Start the Frontend (Terminal 2)

#### 3.1 Open a NEW Terminal Window
Open a second terminal/command prompt window.

#### 3.2 Navigate to Frontend Directory
```bash
cd "F:\TTTR - eKutir Data\Farmer-chat\frontend"
```

#### 3.3 Install Frontend Dependencies (First Time Only)
```bash
npm install
```

This will install:
- ✅ React
- ✅ TypeScript
- ✅ Vite
- ✅ Axios

Wait for installation to complete. You'll see a progress bar and it may take 1-2 minutes.

#### 3.4 Start the Frontend Dev Server
```bash
npm run dev
```

**What you should see:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Keep this terminal window open too!** The frontend must stay running.

---

### Step 4: Open the Application

#### 4.1 Open Your Web Browser
Open Chrome, Firefox, or Edge

#### 4.2 Navigate to the Frontend
```
http://localhost:3000
```

You should see:
- ✅ Green header with "Farmer Chat Assistant"
- ✅ Status indicator showing "34,170 chunks indexed"
- ✅ Welcome message with example questions

#### 4.3 Verify Backend is Running (Optional)
Open a new browser tab:
```
http://localhost:8000
```

You should see a JSON response:
```json
{
  "status": "ready",
  "index_loaded": true,
  "total_chunks": 34170
}
```

---

## Step 5: Test the Chat

### Send a Test Message
1. Type in the chat input: **"What is crop rotation?"**
2. Press **Enter** or click **Send**
3. You should see:
   - Your message appear on the right (blue bubble)
   - Loading dots appear
   - Assistant response appear on the left (green bubble)

---

## Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│                     Terminal 1 (Backend)                     │
│─────────────────────────────────────────────────────────────│
│ F:\TTTR - eKutir Data\Farmer-chat>                          │
│ uvicorn src.api:app --reload --host 0.0.0.0 --port 8000     │
│                                                              │
│ INFO:     Uvicorn running on http://0.0.0.0:8000            │
│ Loaded index with 34170 chunks                              │
│                                                              │
│ [KEEP THIS RUNNING] ← Don't close this window!              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Terminal 2 (Frontend)                     │
│─────────────────────────────────────────────────────────────│
│ F:\TTTR - eKutir Data\Farmer-chat\frontend>                │
│ npm run dev                                                  │
│                                                              │
│ VITE ready in 500 ms                                        │
│ ➜  Local:   http://localhost:3000/                         │
│                                                              │
│ [KEEP THIS RUNNING] ← Don't close this window!              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Browser (localhost:3000)                    │
│─────────────────────────────────────────────────────────────│
│  ╔════════════════════════════════════════════════════════╗ │
│  ║ Farmer Chat Assistant              🟢 34,170 chunks   ║ │
│  ╠════════════════════════════════════════════════════════╣ │
│  ║                                                        ║ │
│  ║  Welcome to Farmer Chat!                              ║ │
│  ║  Ask me anything about farming...                     ║ │
│  ║                                                        ║ │
│  ║                                                        ║ │
│  ║  ┌──────────────────────────────────┐                ║ │
│  ║  │ Type your message...             │  [Send]        ║ │
│  ║  └──────────────────────────────────┘                ║ │
│  ╚════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Problem: Backend won't start

**Error: "ANTHROPIC_API_KEY environment variable is required"**
```bash
# Solution: Check your .env file exists
cat .env

# Make sure it contains:
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Error: "No module named 'fastapi'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error: "Port 8000 is already in use"**
```bash
# Solution: Use a different port
uvicorn src.api:app --reload --port 8001

# Then update frontend/.env to use the new port:
VITE_API_URL=http://localhost:8001
```

---

### Problem: Frontend won't start

**Error: "command not found: npm"**
```bash
# Solution: Install Node.js from https://nodejs.org/
# Then try again
```

**Error: "Cannot find module"**
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Solution: Vite will automatically try 3001, 3002, etc.
# Or specify a port:
npm run dev -- --port 3001
```

---

### Problem: Frontend loads but can't connect to backend

**Error in browser: "No response from server"**

**Check:**
1. ✅ Is Terminal 1 (backend) still running?
2. ✅ Does http://localhost:8000 work in browser?
3. ✅ Any firewall blocking connections?

**Solution:**
```bash
# Restart the backend
# Terminal 1:
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

---

### Problem: Chat sends message but gets error

**Error: "401 authentication_error"**
```bash
# Your API key is invalid
# Update .env with a valid key from https://console.anthropic.com/
```

**Error: "Index file not found"**
```bash
# Rebuild the FAISS index
python -m src.main --build data/transcripts
```

---

## Stopping the Application

### To stop the backend (Terminal 1):
Press `Ctrl + C`

### To stop the frontend (Terminal 2):
Press `Ctrl + C`

---

## Quick Reference Commands

### Backend Commands
```bash
# Start backend
cd "F:\TTTR - eKutir Data\Farmer-chat"
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Rebuild index if needed
python -m src.main --build data/transcripts

# Test backend health
curl http://localhost:8000/health
```

### Frontend Commands
```bash
# Start frontend
cd "F:\TTTR - eKutir Data\Farmer-chat\frontend"
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Summary Checklist

Before you start:
- [ ] Python installed
- [ ] Node.js and npm installed
- [ ] `.env` file has valid ANTHROPIC_API_KEY
- [ ] FAISS index built (34,170 chunks)

To run the app:
- [ ] Terminal 1: Start backend → `uvicorn src.api:app --reload --host 0.0.0.0 --port 8000`
- [ ] Terminal 2: Start frontend → `cd frontend && npm run dev`
- [ ] Browser: Open http://localhost:3000

You should see:
- [ ] Green header with "Farmer Chat Assistant"
- [ ] Status showing chunks indexed
- [ ] Able to send messages and receive responses

---

## Need Help?

If you're still having issues:
1. Check both terminal windows for error messages
2. Verify the FAISS index is built
3. Ensure your API key is valid
4. Try rebuilding dependencies (`pip install -r requirements.txt` and `npm install`)

Happy chatting! 🌾
