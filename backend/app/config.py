"""
Application Configuration
Centralizes all environment variables using Pydantic BaseSettings
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./chatpdf.db"
    
    # Vector Store (ChromaDB)
    chroma_persist_dir: str = "./chroma_db"
    
    # Gemini LLM
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    
    # File Storage
    upload_directory: str = "./uploads"
    max_file_size: int = 10_000_000  # 10MB
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Server
    port: int = 8000
    
    # App Info
    app_name: str = "ChatPDF API"
    app_version: str = "2.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every request.
    """
    return Settings()


# Convenience access
settings = get_settings()
