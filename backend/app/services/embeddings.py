import google.generativeai as genai
import os
import time
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
# We reuse the key from the environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class EmbeddingService:
    def __init__(self):
        # No local model to load! 🚀
        self.model_name = "models/embedding-001"
        print(f"Initialized Gemini Embedding Service with {self.model_name}")

    def embed_text(self, text: str, task_type: str = "retrieval_query") -> List[float]:
        """Embed a single string (query or document)."""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            return result['embedding']
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
                result = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                
                # Handle response structure
                if 'embedding' in result:
                    e = result['embedding']
                    # If we got a list of lists, extend. If we got one list (float), append.
                    # But batch request usually returns list of embeddings.
                    if e and isinstance(e[0], list):
                        embeddings.extend(e)
                    else:
                        embeddings.append(e)
                    
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

