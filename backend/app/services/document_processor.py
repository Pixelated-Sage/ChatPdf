"""
Universal Document Processor
Supports: PDF, DOCX, TXT, MD, HTML
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """Universal document processor for multiple file types."""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'PDF Document',
        '.docx': 'Word Document',
        '.doc': 'Word Document (Legacy)',
        '.txt': 'Text File',
        '.md': 'Markdown File',
        '.html': 'HTML File',
        '.htm': 'HTML File',
    }
    
    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if file type is supported."""
        ext = Path(filename).suffix.lower()
        return ext in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def get_file_type(cls, filename: str) -> Optional[str]:
        """Get human-readable file type."""
        ext = Path(filename).suffix.lower()
        return cls.SUPPORTED_EXTENSIONS.get(ext)
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract all text from any supported document."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return DocumentProcessor._extract_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentProcessor._extract_docx(file_path)
        elif ext in ['.txt', '.md']:
            return DocumentProcessor._extract_text_file(file_path)
        elif ext in ['.html', '.htm']:
            return DocumentProcessor._extract_html(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        import PyPDF2
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            raise ImportError("python-docx is required for DOCX support. Install: pip install python-docx")
    
    @staticmethod
    def _extract_text_file(file_path: str) -> str:
        """Extract text from plain text/markdown files."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    
    @staticmethod
    def _extract_html(file_path: str) -> str:
        """Extract text from HTML files."""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                return soup.get_text(separator='\n', strip=True)
        except ImportError:
            raise ImportError("beautifulsoup4 is required for HTML support. Install: pip install beautifulsoup4")
    
    @staticmethod
    def get_metadata(file_path: str) -> Dict[str, Any]:
        """Get basic metadata from any document."""
        ext = Path(file_path).suffix.lower()
        file_size = os.path.getsize(file_path)
        
        metadata = {
            "file_size": file_size,
            "file_type": DocumentProcessor.SUPPORTED_EXTENSIONS.get(ext, "Unknown"),
        }
        
        # Add page count for PDFs
        if ext == '.pdf':
            import PyPDF2
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                metadata["page_count"] = len(reader.pages)
        else:
            # For non-PDF, estimate pages based on character count
            text = DocumentProcessor.extract_text(file_path)
            # Rough estimate: 2000 chars per page
            metadata["page_count"] = max(1, len(text) // 2000)
        
        return metadata
    
    @staticmethod
    def extract_pages(file_path: str) -> List[Dict[str, Any]]:
        """Extract content with page/section information."""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return DocumentProcessor._extract_pdf_pages(file_path)
        else:
            # For non-PDF, create virtual pages
            return DocumentProcessor._extract_virtual_pages(file_path)
    
    @staticmethod
    def _extract_pdf_pages(file_path: str) -> List[Dict[str, Any]]:
        """Extract PDF pages."""
        import PyPDF2
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
    def _extract_virtual_pages(file_path: str) -> List[Dict[str, Any]]:
        """
        Create virtual pages for non-PDF documents.
        Split by ~2000 character chunks to simulate pages.
        """
        text = DocumentProcessor.extract_text(file_path)
        
        # Split into roughly page-sized chunks
        page_size = 2000
        pages = []
        
        for i in range(0, len(text), page_size):
            chunk = text[i:i + page_size]
            if chunk.strip():
                pages.append({
                    "page_number": (i // page_size) + 1,
                    "content": chunk
                })
        
        # Ensure at least one page
        if not pages and text.strip():
            pages.append({
                "page_number": 1,
                "content": text
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
