from google import genai
from google.genai import types
import os
import time
from typing import List, Union
from dotenv import load_dotenv
from ..config import settings

load_dotenv()


class EmbeddingService:
    def __init__(self):
        # Initialize the new GenAI Client
        if not settings.gemini_api_key:
             # Fallback to os.getenv if settings not ready (though settings should handle it)
             self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        else:
             self.client = genai.Client(api_key=settings.gemini_api_key)
             
        self.model_name = "models/text-embedding-004" # Using newer persistent model if available, or embedding-001
        print(f"Initialized Gemini Embedding Service (google.genai) with {self.model_name}")

    def embed_text(self, text: str, task_type: str = "retrieval_query") -> List[float]:
        """Embed a single string (query or document)."""
        try:
            # New SDK usage
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type
                )
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error embedding text: {e}")
            return [0.0] * 768

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Batch embed multiple strings (documents)."""
        embeddings = []
        batch_size = 10
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="retrieval_document"
                    )
                )
                
                # New SDK returns a list of embedding objects
                if response.embeddings:
                    batch_embeddings = [emb.values for emb in response.embeddings]
                    embeddings.extend(batch_embeddings)
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error batch embedding: {e}")
                # Fallback: one by one
                for text in batch:
                    try:
                        embeddings.append(self.embed_text(text, task_type="retrieval_document"))
                        time.sleep(0.2) 
                    except:
                        embeddings.append([0.0] * 768)
                        
        return embeddings

# Singleton instance
embedding_service = EmbeddingService()

