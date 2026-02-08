from google import genai
from typing import List, Dict, Any, AsyncGenerator
import os
import re
import asyncio
import random
from .embeddings import embedding_service
from .vector_store import vector_store

class ChatService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-flash-lite-latest'
        else:
            self.client = None

    async def generate_answer(
        self, 
        question: str, 
        doc_ids: List[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming answer with citations (Async + Backoff)."""
        if not self.client:
            yield {"type": "error", "content": "GEMINI_API_KEY not configured"}
            return

        # 1. Embed question (blocking call, run in executor if needed, but fast enough for now)
        question_embedding = embedding_service.embed_text(question)

        # 2. Query vector store
        search_results = vector_store.query(question_embedding, n_results=5, doc_ids=doc_ids)
        
        chunks = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]

        # 3. Build context
        context_parts = []
        for i, chunk in enumerate(chunks):
            meta = metadatas[i]
            context_parts.append(f"[Source: {meta['filename']}, Page {meta['page']}]\n{chunk}")
        
        context_text = "\n\n".join(context_parts)
        
        prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context_text}

Question: {question}

Instructions:
- Be concise but complete
- Cite sources using [Filename, Page X] format
- If multiple sources support a point, cite all relevant sources
- Use markdown for formatting

Answer:"""

        # 4. Stream from Gemini with Exponential Backoff
        retries = 3
        base_delay = 1
        response_iterator = None

        for attempt in range(retries):
            try:
                # Use async generation from new SDK
                # client.aio.models.generate_content_stream
                response_iterator = await self.client.aio.models.generate_content_stream(
                    model=self.model_name,
                    contents=prompt
                )
                break
            except Exception as e:
                is_rate_limit = "429" in str(e) or "Resource has been exhausted" in str(e) or "Quota exceeded" in str(e)
                if is_rate_limit and attempt < retries - 1:
                    # Parse "retry in X seconds" if present
                    retry_match = re.search(r"retry in (\d+(\.\d+)?)s", str(e))
                    if retry_match:
                        sleep_time = float(retry_match.group(1)) + 1.0 # Add 1s buffer
                    else:
                        # Fallback exponential backoff
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                    
                    print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                else:
                    yield {"type": "error", "content": f"Rate limit exceeded. Please try again later. ({str(e)})"}
                    return

        if not response_iterator:
             return

        try:
            full_content = ""
            async for chunk in response_iterator:
                if chunk.text:
                    full_content += chunk.text
                    yield {"type": "chunk", "content": chunk.text}
            
            # 5. Parse Citations
            citations = self.parse_citations(full_content, metadatas, chunks)
            for citation in citations:
                yield {"type": "citation", "data": citation}
            
            yield {"type": "done", "full_content": full_content, "citations": citations}

        except Exception as e:
            yield {"type": "error", "content": str(e)}

    def parse_citations(self, text: str, metadatas: List[Dict[str, Any]], chunks: List[str]) -> List[Dict[str, Any]]:
        """Extract [Filename, Page X] citations and match with metadata."""
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
                if meta['filename'] == filename and meta['page'] == page:
                    found.append({
                        "document_id": meta['document_id'],
                        "filename": filename,
                        "page": page,
                        "chunk_text": chunk[:200] + "..." # Preview
                    })
                    seen.add(citation_key)
                    break
        return found

    def generate_title(self, first_message: str) -> str:
        """Generate a short title based on the first user message."""
        if not self.client:
            return "New Conversation"
        try:
            prompt = f"Generate a short, concise 3-5 word title for a conversation that starts with: '{first_message}'. Respond only with the title, no quotes or explanations."
            # Sync call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            title = response.text.strip().replace('"', '')
            return title[:50]
        except Exception as e:
            print(f"Error generating title: {e}")
            return "New Conversation"

# Singleton instance
chat_service = ChatService()
