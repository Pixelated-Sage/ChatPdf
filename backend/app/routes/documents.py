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
    """
    Delete a document and all associated resources:
    - Physical file from disk
    - Vector embeddings from ChromaDB
    - Database record
    """
    db_doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    deletion_status = {
        "file_deleted": False,
        "vectors_deleted": False,
        "db_deleted": False,
        "errors": []
    }
    
    # 1. Delete file from filesystem
    if db_doc.file_path:
        try:
            if os.path.exists(db_doc.file_path):
                os.remove(db_doc.file_path)
                deletion_status["file_deleted"] = True
                print(f"✅ Deleted file: {db_doc.file_path}")
            else:
                deletion_status["errors"].append(f"File not found: {db_doc.file_path}")
                print(f"⚠️  File already deleted or not found: {db_doc.file_path}")
        except Exception as e:
            error_msg = f"Failed to delete file: {str(e)}"
            deletion_status["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    # 2. Delete vectors from vector store
    from ..services.vector_store import vector_store
    try:
        vector_store.delete_document(document_id)
        deletion_status["vectors_deleted"] = True
        print(f"✅ Deleted vectors for document: {document_id}")
    except Exception as e:
        error_msg = f"Failed to delete vectors: {str(e)}"
        deletion_status["errors"].append(error_msg)
        print(f"❌ {error_msg}")

    # 3. Delete from database
    try:
        db.delete(db_doc)
        db.commit()
        deletion_status["db_deleted"] = True
        print(f"✅ Deleted database record: {document_id}")
    except Exception as e:
        error_msg = f"Failed to delete database record: {str(e)}"
        deletion_status["errors"].append(error_msg)
        print(f"❌ {error_msg}")
        db.rollback()
        raise HTTPException(status_code=500, detail=error_msg)
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": db_doc.original_filename,
        "status": deletion_status
    }


@router.get("/documents/storage/stats")
async def get_storage_stats(db: Session = Depends(get_db)):
    """
    Get storage statistics:
    - Total files on disk
    - Total documents in database
    - Orphaned files (on disk but not in DB)
    - Total disk usage
    """
    from pathlib import Path
    from ..config import settings
    
    upload_dir = Path(settings.upload_directory)
    
    if not upload_dir.exists():
        return {
            "error": "Upload directory does not exist",
            "path": str(upload_dir)
        }
    
    # Count files on disk
    files_on_disk = list(upload_dir.glob("*"))
    disk_files = [f for f in files_on_disk if f.is_file()]
    
    # Count documents in database
    db_docs = db.query(models.Document).all()
    db_file_paths = {doc.file_path for doc in db_docs}
    
    # Find orphaned files
    orphaned = [f for f in disk_files if str(f) not in db_file_paths]
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in disk_files)
    orphaned_size = sum(f.stat().st_size for f in orphaned)
    
    return {
        "upload_directory": str(upload_dir),
        "total_files_on_disk": len(disk_files),
        "total_documents_in_db": len(db_docs),
        "orphaned_files": len(orphaned),
        "orphaned_file_paths": [str(f) for f in orphaned[:10]],  # Show first 10
        "total_disk_usage_mb": round(total_size / (1024 * 1024), 2),
        "orphaned_disk_usage_mb": round(orphaned_size / (1024 * 1024), 2)
    }


@router.post("/documents/storage/cleanup")
async def cleanup_orphaned_files(db: Session = Depends(get_db)):
    """
    Delete orphaned files (files on disk with no database record).
    Use with caution!
    """
    from pathlib import Path
    from ..config import settings
    
    upload_dir = Path(settings.upload_directory)
    
    if not upload_dir.exists():
        raise HTTPException(status_code=404, detail="Upload directory not found")
    
    # Get all files on disk
    files_on_disk = list(upload_dir.glob("*"))
    disk_files = [f for f in files_on_disk if f.is_file()]
    
    # Get all file paths from database
    db_docs = db.query(models.Document).all()
    db_file_paths = {doc.file_path for doc in db_docs}
    
    # Find orphaned files
    orphaned = [f for f in disk_files if str(f) not in db_file_paths]
    
    deleted_files = []
    errors = []
    
    for file_path in orphaned:
        try:
            file_size = file_path.stat().st_size
            os.remove(file_path)
            deleted_files.append({
                "path": str(file_path),
                "size_mb": round(file_size / (1024 * 1024), 2)
            })
            print(f"✅ Cleaned up orphaned file: {file_path}")
        except Exception as e:
            errors.append({
                "path": str(file_path),
                "error": str(e)
            })
            print(f"❌ Failed to delete {file_path}: {e}")
    
    total_freed_mb = sum(f["size_mb"] for f in deleted_files)
    
    return {
        "message": "Cleanup completed",
        "deleted_count": len(deleted_files),
        "deleted_files": deleted_files,
        "errors": errors,
        "total_freed_mb": round(total_freed_mb, 2)
    }
