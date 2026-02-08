import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import upload, documents, chat, conversations

# Check for required environment variables
if not os.getenv("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY is not set. Chat functionality will fail.")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatPDF API")

# Sanitize CORS: Allow localhost for development and common production domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://chatpdf.vercel.app", # Placeholder for your production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")

@app.get("/api/debug/vectors")
async def debug_vectors():
    from .services.vector_store import vector_store
    import inspect
    try:
        return {
            "type": str(type(vector_store.client)),
            "query_points_spec": str(inspect.signature(vector_store.client.query_points))
        }
    except Exception as e:
        return {"error": str(e)}
# chat.router might be empty for now, but let's include it if it exists
try:
    app.include_router(chat.router, prefix="/api")
except AttributeError:
    pass

@app.get("/")
async def root():
    return {"message": "Welcome to ChatPDF API"}
