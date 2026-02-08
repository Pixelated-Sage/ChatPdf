from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List
import os

# CRITICAL: Load model once, reuse
# Global rules say store models in /data/models
MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL_DIR = Path("/data/models/embeddings")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / MODEL_NAME

class EmbeddingService:
    def __init__(self):
        if not MODEL_PATH.exists():
            print(f"Downloading model {MODEL_NAME} to {MODEL_PATH}...")
            self.model = SentenceTransformer(MODEL_NAME)
            self.model.save(str(MODEL_PATH))
        else:
            print(f"Loading model from {MODEL_PATH}...")
            self.model = SentenceTransformer(str(MODEL_PATH))

    def embed_text(self, text: str) -> List[float]:
        """Embed a single string."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Batch embed multiple strings for speed."""
        embeddings = self.model.encode(
            chunks,
            batch_size=32,
            show_progress_bar=False
        )
        return embeddings.tolist()

# Singleton instance
embedding_service = EmbeddingService()
