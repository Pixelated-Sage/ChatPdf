"""
Chat Service for ChatPDF
Handles RAG pipeline: embed question → query vectors → generate answer with Gemini
"""
from typing import List, Dict, Any, AsyncGenerator
import re

from .embeddings import embedding_service
from .vector_store import vector_store
from .llm import gemini_client


class ChatService:
    def __init__(self):
        self.llm = gemini_client
    
    async def generate_answer(
        self, 
        question: str, 
        doc_ids: List[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming answer with citations using Gemini.
        
        Args:
            question: User's question
            doc_ids: Optional list of document IDs to search within
            
        Yields:
            dict: Stream events with type and content
        """
        # 1. Embed question
        try:
            question_embedding = embedding_service.embed_text(question)
        except Exception as e:
            yield {"type": "error", "content": f"Embedding failed: {str(e)}"}
            return

        # 2. Query vector store
        try:
            search_results = vector_store.query(
                question_embedding, 
                n_results=5, 
                doc_ids=doc_ids
            )
        except Exception as e:
            yield {"type": "error", "content": f"Vector search failed: {str(e)}"}
            return
        
        chunks = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        if not chunks:
            yield {
                "type": "chunk", 
                "content": "No relevant documents found. Please upload some PDFs first."
            }
            yield {"type": "done", "full_content": "", "citations": []}
            return

        # 3. Build context for RAG prompt
        context_chunks = []
        for chunk, meta in zip(chunks, metadatas):
            context_chunks.append({
                "text": chunk,
                "filename": meta.get("filename", "Unknown"),
                "page": meta.get("page", 0)
            })
        
        prompt = self.llm.build_rag_prompt(question, context_chunks)

        # 4. Stream from Gemini (native async)
        try:
            full_content = ""
            
            async for token in self.llm.generate_stream(prompt):
                full_content += token
                yield {"type": "chunk", "content": token}
            
            # 5. Parse Citations
            citations = self.parse_citations(full_content, metadatas, chunks)
            for citation in citations:
                yield {"type": "citation", "data": citation}
            
            yield {
                "type": "done", 
                "full_content": full_content, 
                "citations": citations
            }

        except Exception as e:
            yield {"type": "error", "content": f"Generation failed: {str(e)}"}

    def parse_citations(
        self, 
        text: str, 
        metadatas: List[Dict[str, Any]], 
        chunks: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract [Filename, Page X] citations and match with metadata.
        
        Args:
            text: Generated response text
            metadatas: List of chunk metadata from vector store
            chunks: List of chunk texts
            
        Returns:
            List of citation dicts with document info
        """
        pattern = r'\[([^,]+),\s*Page\s*(\d+)\]'
        found = []
        seen = set()
        
        for match in re.finditer(pattern, text):
            filename = match.group(1).strip()
            page = int(match.group(2))
            
            citation_key = f"{filename}_{page}"
            if citation_key in seen:
                continue
                
            # Find matching chunk in search results
            for meta, chunk in zip(metadatas, chunks):
                if meta.get('filename') == filename and meta.get('page') == page:
                    found.append({
                        "document_id": meta.get('document_id', ''),
                        "filename": filename,
                        "page": page,
                        "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                    })
                    seen.add(citation_key)
                    break
        return found

    def generate_title(self, first_message: str) -> str:
        """
        Generate a short title based on the first user message.
        
        Args:
            first_message: The user's first question
            
        Returns:
            str: Short conversation title (3-5 words)
        """
        try:
            prompt = (
                f"Generate a short, concise 3-5 word title for a conversation "
                f"that starts with: '{first_message}'. "
                f"Respond only with the title, no quotes or explanations."
            )
            title = self.llm.generate(prompt)
            # Clean up response
            title = title.strip().replace('"', '').replace("'", "")
            # Truncate if too long
            return title[:50] if title else "New Conversation"
        except Exception as e:
            print(f"Error generating title: {e}")
            return "New Conversation"


# Singleton instance
chat_service = ChatService()
