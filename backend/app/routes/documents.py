from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["documents"])

@router.get("/documents", response_model=List[schemas.Document])
async def list_documents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return documents

@router.get("/documents/{document_id}", response_model=schemas.Document)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    if db_doc.file_path and os.path.exists(db_doc.file_path):
        os.remove(db_doc.file_path)
    
    # Delete vectors from vector store
    from ..services.vector_store import vector_store
    try:
        vector_store.delete_document(document_id)
    except Exception as e:
        print(f"Error deleting vectors for {document_id}: {e}")

    # Delete from database
    db.delete(db_doc)
    db.commit()
    
    return {"message": "Document deleted successfully", "document_id": document_id}
