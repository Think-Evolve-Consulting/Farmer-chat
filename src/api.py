"""FastAPI REST API for the Farmer Chat Interface."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from .chat_client import FarmerChatClient
from .retriever import ContextRetriever
from .conversation_logger import ConversationLogger
from .config import config


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    response: str
    has_context: bool


class StatusResponse(BaseModel):
    status: str
    index_loaded: bool
    total_chunks: Optional[int] = None


# Initialize FastAPI app
app = FastAPI(
    title="Farmer Chat API",
    description="REST API for farmer chat interface with RAG capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chat client instance (maintains conversation history)
chat_client: Optional[FarmerChatClient] = None
conversation_logger: Optional[ConversationLogger] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the chat client on startup."""
    global chat_client, conversation_logger

    # Validate config
    try:
        config.validate()
    except ValueError as e:
        print(f"Warning: {e}")

    # Initialize logger
    if config.conversation_logging_enabled:
        conversation_logger = ConversationLogger(log_dir=config.conversation_log_dir)

    # Initialize client with logger
    chat_client = FarmerChatClient(logger=conversation_logger)

    # Load index
    if not chat_client.retriever.load_index():
        print("Warning: No index found. Context retrieval will be disabled.")
    else:
        print(f"Loaded index with {chat_client.retriever.indexer.total_chunks} chunks")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global conversation_logger

    if conversation_logger:
        conversation_logger.close()


@app.get("/", response_model=StatusResponse)
async def root():
    """Get API status."""
    if chat_client is None:
        raise HTTPException(status_code=500, detail="Chat client not initialized")

    index_loaded = chat_client.retriever.indexer is not None
    total_chunks = chat_client.retriever.indexer.total_chunks if index_loaded else None

    return StatusResponse(
        status="ready",
        index_loaded=index_loaded,
        total_chunks=total_chunks
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response.

    Args:
        request: ChatRequest with message and context flag

    Returns:
        ChatResponse with assistant's response
    """
    if chat_client is None:
        raise HTTPException(status_code=500, detail="Chat client not initialized")

    try:
        response = chat_client.chat(
            user_message=request.message,
            include_context=request.include_context
        )

        return ChatResponse(
            response=response,
            has_context=request.include_context and chat_client.retriever.indexer is not None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear")
async def clear_history():
    """Clear the conversation history."""
    if chat_client is None:
        raise HTTPException(status_code=500, detail="Chat client not initialized")

    chat_client.clear_history()
    return {"message": "Conversation history cleared"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
