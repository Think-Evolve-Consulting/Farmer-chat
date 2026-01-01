# Farmer Chat Frontend

A modern, responsive TypeScript React frontend for the Farmer Chat RAG system.

## Features

- 💬 Real-time chat interface
- 🎨 Clean, responsive design
- 📱 Mobile-friendly
- 🔄 Conversation history
- 📊 Index status display
- ⚡ Fast and lightweight (Vite + React)

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS3** - Styling with CSS variables

## Prerequisites

- Node.js 16+ and npm
- Python backend running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start dev server (http://localhost:3000)
npm run dev
```

The dev server includes:
- Hot module replacement (HMR)
- Proxy to backend API at localhost:8000
- TypeScript type checking

## Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── ChatMessage.tsx      # Individual message display
│   │   └── ChatInput.tsx        # User input component
│   ├── services/
│   │   └── api.ts               # API client
│   ├── types/
│   │   └── index.ts             # TypeScript interfaces
│   ├── App.tsx                  # Root component
│   ├── App.css                  # Main styles
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── public/                      # Static assets
├── index.html                   # HTML template
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript config
└── package.json                # Dependencies

```

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `GET /` - Get API status and index info
- `POST /chat` - Send message and receive response
- `POST /clear` - Clear conversation history
- `GET /health` - Health check

## Environment Variables

Create a `.env` file to customize the API URL:

```env
VITE_API_URL=http://localhost:8000
```

## Usage

1. **Start the backend**:
   ```bash
   cd ..
   uvicorn src.api:app --reload
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. **Open browser** to http://localhost:3000

4. **Start chatting** with the farming assistant!

## Features in Detail

### Chat Interface
- Clean, modern design with agricultural color scheme
- Real-time message updates
- Automatic scroll to latest message
- Loading indicators during API calls

### Message Display
- User messages on the right (blue background)
- Assistant messages on the left (green background)
- Timestamp for each message
- Smooth animations

### Status Display
- Shows if FAISS index is loaded
- Displays total number of indexed chunks
- Visual indicator (green dot when active)

### Error Handling
- Clear error messages
- Connection status notifications
- Graceful fallbacks

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in input

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

When making changes:
1. Use TypeScript for type safety
2. Follow React best practices
3. Keep components modular
4. Add appropriate error handling
5. Test responsive design

## License

Part of the Farmer Chat RAG system.
