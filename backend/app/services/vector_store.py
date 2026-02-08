from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import time

# Abhishek's partition structure
QDRANT_DATA_PATH = Path("/data/qdrant_db")
QDRANT_DATA_PATH.mkdir(parents=True, exist_ok=True)

class VectorStore:
    def __init__(self):
        # Local storage mode with retry mechanism for locking
        self.client = self._initialize_client()
        self.collection_name = "document_chunks"
        
        self._ensure_collection()

    def _initialize_client(self, retries=3, delay=1.0) -> QdrantClient:
        """Initialize QdrantClient with retries for file locking."""
        last_error = None
        for attempt in range(retries):
            try:
                return QdrantClient(path=str(QDRANT_DATA_PATH))
            except Exception as e:
                last_error = e
                # Check for BlockingIOError or similar locking issues
                if "Resource temporarily unavailable" in str(e) or "already accessed" in str(e):
                    print(f"Vector store locked. Retrying in {delay}s (Attempt {attempt+1}/{retries})...")
                    time.sleep(delay)
                else:
                    raise e
        
        # Fallback to in-memory if persistent storage fails (optional, but safer to just fail)
        print(f"Failed to acquire lock for {QDRANT_DATA_PATH}. Error: {last_error}")
        raise RuntimeError(f"Could not initialize Vector Store. Ensure no other active processes are using {QDRANT_DATA_PATH}. \nTip: Kill other uvicorn/python processes.")

    def _ensure_collection(self):
        # Create collection if it doesn't exist
        # all-MiniLM-L6-v2 has 384 dimensions
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=384, 
                        distance=rest_models.Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            # If we can't check/create, the client might be unusable

    def add_chunks(
        self, 
        doc_id: str, 
        chunks: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]]
    ):
        """Add document chunks to the vector store."""
        import uuid
        points = []
        for i, (chunk, embedding, metadata) in enumerate(zip(chunks, embeddings, metadatas)):
            # Combine chunk text into metadata for retrieval
            payload = {**metadata, "content": chunk}
            # Generate a deterministic UUID for the point ID
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}_{i}"))
            points.append(
                rest_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def query(self, query_embedding: List[float], n_results: int = 5, doc_ids: List[str] = None) -> Dict[str, Any]:
        """Query the vector store for similar chunks."""
        filter_obj = None
        if doc_ids:
            filter_obj = rest_models.Filter(
                must=[
                    rest_models.FieldCondition(
                        key="document_id",
                        match=rest_models.MatchAny(any=doc_ids)
                    )
                ]
            )
        
        # Use query_points which is available in Abhishek's current qdrant-client version
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=filter_obj,
            limit=n_results
        )
        points = response.points
        
        # Format results to match previous interface
        formatted = {
            "documents": [[r.payload["content"] for r in points]],
            "metadatas": [[{k: v for k, v in r.payload.items() if k != "content"} for r in points]]
        }
        return formatted

    def delete_document(self, doc_id: str):
        """Remove all chunks associated with a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest_models.FilterSelector(
                filter=rest_models.Filter(
                    must=[
                        rest_models.FieldCondition(
                            key="document_id",
                            match=rest_models.MatchValue(value=doc_id)
                        )
                    ]
                )
            )
        )

# Singleton instance
vector_store = VectorStore()
