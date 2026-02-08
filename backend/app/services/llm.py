"""
Gemini LLM Client for ChatPDF
Provides async streaming responses via Google GenAI SDK
"""
from google import genai
from typing import AsyncGenerator, List, Dict, Any
import asyncio

from ..config import settings


class GeminiClient:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
    
    async def generate_stream(
        self, 
        prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Gemini.
        
        Args:
            prompt: The user prompt/question with context
            
        Yields:
            str: Token chunks from the LLM
        """
        try:
            response = await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_output_tokens": 2048,
                }
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"[Error: Gemini API failed - {str(e)}]"
    
    def generate(self, prompt: str) -> str:
        """
        Non-streaming generation (for title generation, etc.)
        
        Args:
            prompt: The prompt
            
        Returns:
            str: Complete response text
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_output_tokens": 100,
                }
            )
            return response.text or ""
        except Exception as e:
            return f"Error: {str(e)}"

    def build_rag_prompt(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Build the RAG prompt with context chunks.
        
        Args:
            question: User's question
            context_chunks: List of dicts with 'text', 'filename', 'page' keys
            
        Returns:
            str: Formatted prompt for the LLM
        """
        context_parts = []
        for chunk in context_chunks:
            source = f"[Source: {chunk['filename']}, Page {chunk['page']}]"
            context_parts.append(f"{source}\n{chunk['text']}")
        
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
        return prompt


# Singleton instance
gemini_client = GeminiClient()
