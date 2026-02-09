"""
ChatPDF API - Main Application Entry Point
FastAPI app with CORS, routes, and health endpoints
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import upload, documents, chat, conversations
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.upload_directory, exist_ok=True)
    print(f"✅ Uploads directory ready: {settings.upload_directory}")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Check Gemini API key
    if settings.gemini_api_key:
        print(f"✅ Gemini API key configured (model: {settings.gemini_model})")
    else:
        print("⚠️  GEMINI_API_KEY not set in environment")
    
    # Check ChromaDB
    from .services.vector_store import vector_store
    stats = vector_store.get_collection_stats()
    print(f"✅ ChromaDB ready ({stats['count']} chunks in collection)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS Configuration
# Allow any localhost port for development and the production domain
allow_origin_regex = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
origins = [
    "http://localhost:3000",
    "https://chat-pdf-neon.vercel.app", # Explicitly allow production frontend
    settings.frontend_url,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for production monitoring.
    Returns status of all services.
    """
    from .services.vector_store import vector_store
    
    # Check Gemini API key
    gemini_status = "healthy" if settings.gemini_api_key else "missing_api_key"
    
    # Check ChromaDB
    try:
        stats = vector_store.get_collection_stats()
        chroma_status = "healthy"
        chroma_count = stats["count"]
    except Exception as e:
        chroma_status = f"error: {str(e)}"
        chroma_count = 0
    
    # Check uploads directory
    uploads_dir = settings.upload_directory
    uploads_status = "healthy" if os.path.exists(uploads_dir) else "missing"
    
    overall = "healthy" if all([
        gemini_status == "healthy",
        chroma_status == "healthy",
        uploads_status == "healthy"
    ]) else "degraded"
    
    return {
        "status": overall,
        "version": settings.app_version,
        "services": {
            "gemini": {
                "status": gemini_status,
                "model": settings.gemini_model
            },
            "chromadb": {
                "status": chroma_status,
                "path": settings.chroma_persist_dir,
                "chunks": chroma_count
            },
            "storage": {
                "status": uploads_status,
                "path": uploads_dir
            }
        }
    }


@app.get("/api/debug/vectors")
async def debug_vectors():
    """Debug endpoint to check vector store status."""
    from .services.vector_store import vector_store
    try:
        stats = vector_store.get_collection_stats()
        return {
            "collection": stats["name"],
            "chunks": stats["count"],
            "persist_dir": settings.chroma_persist_dir
        }
    except Exception as e:
        return {"error": str(e)}
