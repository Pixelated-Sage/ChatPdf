from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List
import os

# CRITICAL: Load model once, reuse
# Global rules say store models in /data/models, BUT fallback to local for containers
MODEL_NAME = 'all-MiniLM-L6-v2'

# Check if we are in a container or if /data exists
if os.path.exists("/data/models"):
    MODEL_DIR = Path("/data/models/embeddings")
else:
    # Fallback to local app directory for container/deployment
    MODEL_DIR = Path("./models/embeddings")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / MODEL_NAME

class EmbeddingService:
    def __init__(self):
        try:
            if MODEL_PATH.exists():
                print(f"Loading model from {MODEL_PATH}...")
                self.model = SentenceTransformer(str(MODEL_PATH))
            else:
                print(f"Downloading model {MODEL_NAME} to {MODEL_PATH}...")
                self.model = SentenceTransformer(MODEL_NAME)
                self.model.save(str(MODEL_PATH))
        except Exception as e:
            print(f"Error loading model from {MODEL_PATH}, falling back to default cache: {e}")
            self.model = SentenceTransformer(MODEL_NAME)


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
