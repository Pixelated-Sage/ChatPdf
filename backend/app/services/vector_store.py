"""
vector_store.py
Embedded mode - no external server required
"""
# Fix for ChromaDB + Railway (requires SQLite > 3.35)
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
from typing import List, Dict, Any
from pathlib import Path

from ..config import settings


class VectorStore:
    def __init__(self):
        # Ensure persist directory exists
        persist_path = Path(settings.chroma_persist_dir)
        persist_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=str(persist_path))
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self, 
        doc_id: str, 
        chunks: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]]
    ):
        """Add document chunks to the vector store."""
        # Generate unique IDs for each chunk
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Add document_id to each metadata
        for meta in metadatas:
            meta["document_id"] = doc_id
        
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def query(
        self, 
        query_embedding: List[float], 
        n_results: int = 5, 
        doc_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Query the vector store for similar chunks."""
        where_filter = None
        if doc_ids:
            where_filter = {"document_id": {"$in": doc_ids}}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas"]
        )
        
        # Format results to match expected interface
        return {
            "documents": results.get("documents", [[]]),
            "metadatas": results.get("metadatas", [[]])
        }

    def delete_document(self, doc_id: str):
        """Remove all chunks associated with a document."""
        # Get all chunks for this document
        results = self.collection.get(
            where={"document_id": doc_id},
            include=[]
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics for health checks."""
        return {
            "name": self.collection.name,
            "count": self.collection.count()
        }


# Singleton instance
vector_store = VectorStore()
