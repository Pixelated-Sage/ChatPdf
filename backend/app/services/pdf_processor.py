import PyPDF2
from typing import List, Dict, Any
from pathlib import Path
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFProcessor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract all text from a PDF file."""
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def get_metadata(file_path: str) -> Dict[str, Any]:
        """Get basic metadata from a PDF file."""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            return {
                "page_count": len(reader.pages),
                "file_size": os.path.getsize(file_path)
            }

    @staticmethod
    def extract_pages(file_path: str) -> List[Dict[str, Any]]:
        """Extract text page by page with page numbers."""
        pages = []
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    pages.append({
                        "page_number": i + 1,
                        "content": page_text
                    })
        return pages

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """Split text into chunks using LangChain."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
