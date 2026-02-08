from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.pdf_processor import PDFProcessor
from ..services.embeddings import embedding_service
from ..services.vector_store import vector_store
import uuid
import os
from pathlib import Path

router = APIRouter(tags=["upload"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def process_pdf_background(doc_id: str, filename: str, file_path: str, db: Session):
    try:
        # 1. Extract text and pages
        doc_data = PDFProcessor.extract_pages(file_path)
        
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        
        # 2. Process each page
        for page in doc_data:
            chunks = PDFProcessor.chunk_text(page["content"])
            if not chunks:
                continue
                
            embeddings = embedding_service.embed_chunks(chunks)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_embeddings.append(embeddings[i])
                all_metadatas.append({
                    "document_id": doc_id,
                    "filename": filename,
                    "page": page["page_number"],
                    "chunk_index": i
                })
        
        # 3. Store in Vector DB
        if all_chunks:
            vector_store.add_chunks(doc_id, all_chunks, all_embeddings, all_metadatas)
        
        # 4. Update Database
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if doc:
            doc.processed = True
            doc.chunk_count = len(all_chunks)
            db.commit()
            
    except Exception as e:
        print(f"Error processing document {doc_id}: {str(e)}")
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if doc:
            doc.processing_error = str(e)
            db.commit()

@router.post("/upload", response_model=schemas.UploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension and magic bytes
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read the first few bytes to check for PDF magic number
    header = await file.read(4)
    await file.seek(0) # Reset file pointer
    if header != b"%PDF":
        raise HTTPException(status_code=400, detail="Invalid PDF file content")

    # 2. Validate file size (FastAPI doesn't do this automatically for SpoofFile)
    # We can check content length if provided, or read a bit
    # For now, let's just save and check size
    
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    saved_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
             raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        # 3. Get metadata
        metadata = PDFProcessor.get_metadata(str(file_path))
        
        # 4. Create database entry
        db_doc = models.Document(
            id=file_id,
            filename=saved_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=metadata["file_size"],
            page_count=metadata["page_count"],
            processed=False
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # 5. Queue background processing
        background_tasks.add_task(process_pdf_background, file_id, file.filename, str(file_path), db)

        return {
            "document_id": file_id,
            "filename": file.filename,
            "status": "processing",
            "message": "Document uploaded and queued for processing"
        }

    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
