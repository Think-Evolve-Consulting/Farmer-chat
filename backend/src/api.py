"""FastAPI REST API for the Farmer Chat Interface."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path

from .chat_client import FarmerChatClient
from .retriever import ContextRetriever
from .conversation_logger import ConversationLogger
from .product_retriever import ProductRetriever
from .product_logger import ProductLogger
from .config import config


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    response: str
    has_context: bool
    context_results: List[Dict[str, Any]] = []
    products: List[Dict[str, Any]] = []


class StatusResponse(BaseModel):
    status: str
    index_loaded: bool
    total_chunks: Optional[int] = None
    products_available: int = 0


# Initialize FastAPI app
app = FastAPI(
    title="Farmer Chat API",
    description="REST API for farmer chat interface with RAG capabilities",
    version="1.0.0"
)

# Serve local product images for frontend cards/modals.
# This expects images in backend/data/transcripts/FIL Product
_product_image_dir = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "FIL Product"
if _product_image_dir.exists() and _product_image_dir.is_dir():
    # Serve both paths:
    # - /api/product-images/* (direct backend calls)
    # - /product-images/* (Vite proxy with /api prefix rewrite)
    app.mount("/api/product-images", StaticFiles(directory=str(_product_image_dir)), name="product-images-api")
    app.mount("/product-images", StaticFiles(directory=str(_product_image_dir)), name="product-images")
else:
    print(f"[WARN] Product image directory not found: {_product_image_dir}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://misa.thinkevolvelabs.com"  # Cloudflare tunnel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
chat_client: Optional[FarmerChatClient] = None
conversation_logger: Optional[ConversationLogger] = None
product_retriever: Optional[ProductRetriever] = None
product_logger: Optional[ProductLogger] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the chat client and product retriever on startup."""
    global chat_client, conversation_logger, product_retriever, product_logger

    # Validate config
    try:
        config.validate()
    except ValueError as e:
        print(f"Warning: {e}")

    # Initialize conversation logger
    if config.conversation_logging_enabled:
        conversation_logger = ConversationLogger(
            log_dir=config.conversation_log_dir,
            model_name=config.claude_model
        )

    # Initialize chat client with logger
    chat_client = FarmerChatClient(logger=conversation_logger)

    # Load transcript index
    if not chat_client.retriever.load_index():
        print("Warning: No transcript index found. Context retrieval will be disabled.")
    else:
        print(f"[OK] Loaded transcript index with {chat_client.retriever.indexer.total_chunks} chunks")
    
    # Initialize product retriever
    try:
        product_retriever = ProductRetriever()
        print(f"[OK] Product retriever initialized with {product_retriever.total_products} products")
    except Exception as e:
        print(f"[WARN] Error initializing product retriever: {e}")
    
    # Initialize product logger
    product_logger = ProductLogger()


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
    products_available = product_retriever.total_products if product_retriever else 0

    return StatusResponse(
        status="ready",
        index_loaded=index_loaded,
        total_chunks=total_chunks,
        products_available=products_available
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response with relevant products.

    Args:
        request: ChatRequest with message and context flag

    Returns:
        ChatResponse with assistant's response and recommended products
    """
    if chat_client is None:
        raise HTTPException(status_code=500, detail="Chat client not initialized")

    try:
        # Get chat response from transcripts
        response_text, context_results = chat_client.chat(
            user_message=request.message,
            include_context=request.include_context
        )

        # Get relevant products
        products = []
        if product_retriever:
            try:
                products = product_retriever.retrieve(request.message, top_k=3)
                # Log the product recommendation
                if product_logger:
                    product_logger.log_recommendation(
                        query=request.message,
                        products=products
                    )
            except Exception as e:
                print(f"Error retrieving products: {e}")

        return ChatResponse(
            response=response_text,
            has_context=request.include_context and chat_client.retriever.indexer is not None,
            context_results=context_results,
            products=products
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


@app.post("/products/search")
async def search_products(query: str, top_k: int = 5):
    """
    Search for products by query.
    
    Args:
        query: Search query
        top_k: Number of products to return
    
    Returns:
        List of matching products
    """
    if not product_retriever:
        raise HTTPException(status_code=500, detail="Product retriever not initialized")
    
    try:
        products = product_retriever.retrieve(query, top_k=top_k)
        return {"query": query, "products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/by-crop/{crop}")
async def get_products_by_crop(crop: str, top_k: int = 5):
    """
    Get products applicable for a specific crop.
    
    Args:
        crop: Crop name
        top_k: Number of products to return
    
    Returns:
        List of products for the crop
    """
    if not product_retriever:
        raise HTTPException(status_code=500, detail="Product retriever not initialized")
    
    try:
        products = product_retriever.search_by_crop(crop, top_k=top_k)
        return {"crop": crop, "products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/by-disease/{disease}")
async def get_products_by_disease(disease: str, top_k: int = 5):
    """
    Get products that treat a specific disease.
    
    Args:
        disease: Disease name
        top_k: Number of products to return
    
    Returns:
        List of products for the disease
    """
    if not product_retriever:
        raise HTTPException(status_code=500, detail="Product retriever not initialized")
    
    try:
        products = product_retriever.search_by_disease(disease, top_k=top_k)
        return {"disease": disease, "products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/stats")
async def get_product_stats():
    """
    Get statistics about product recommendations.
    
    Returns:
        Product recommendation statistics
    """
    if not product_logger:
        raise HTTPException(status_code=500, detail="Product logger not initialized")
    
    try:
        stats = product_logger.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
