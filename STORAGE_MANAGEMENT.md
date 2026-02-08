# Document Deletion & Storage Management

## Overview

The backend now properly handles complete document deletion with automatic cleanup of all associated resources.

## What Gets Deleted

When a user deletes a document from the frontend, the backend automatically removes:

1. **Physical File** - The uploaded document from disk (`./uploads/`)
2. **Vector Embeddings** - All chunks from ChromaDB vector store
3. **Database Record** - The document metadata from SQLite

## Enhanced Delete Endpoint

**Endpoint**: `DELETE /api/documents/{document_id}`

### Features:

- ✅ Comprehensive cleanup of all resources
- ✅ Detailed status reporting for each deletion step
- ✅ Error handling with rollback on database failures
- ✅ Console logging for debugging

### Response Example:

```json
{
  "message": "Document deleted successfully",
  "document_id": "abc-123",
  "filename": "research_paper.pdf",
  "status": {
    "file_deleted": true,
    "vectors_deleted": true,
    "db_deleted": true,
    "errors": []
  }
}
```

## Storage Management Endpoints

### 1. Get Storage Statistics

**Endpoint**: `GET /api/documents/storage/stats`

Check disk usage and identify orphaned files (files on disk without database records).

```bash
curl http://localhost:8000/api/documents/storage/stats
```

**Response**:

```json
{
  "upload_directory": "./uploads",
  "total_files_on_disk": 7,
  "total_documents_in_db": 2,
  "orphaned_files": 5,
  "orphaned_file_paths": ["uploads/old-file.pdf", "..."],
  "total_disk_usage_mb": 0.07,
  "orphaned_disk_usage_mb": 0.03
}
```

### 2. Cleanup Orphaned Files

**Endpoint**: `POST /api/documents/storage/cleanup`

Remove files that exist on disk but have no database record. Use with caution!

```bash
curl -X POST http://localhost:8000/api/documents/storage/cleanup
```

**Response**:

```json
{
  "message": "Cleanup completed",
  "deleted_count": 5,
  "deleted_files": [{ "path": "uploads/old-file.pdf", "size_mb": 0.01 }],
  "errors": [],
  "total_freed_mb": 0.03
}
```

## Logging

All deletion operations are logged to the console:

```
✅ Deleted file: uploads/abc-123.pdf
✅ Deleted vectors for document: abc-123
✅ Deleted database record: abc-123
```

Errors are clearly marked:

```
❌ Failed to delete file: Permission denied
⚠️  File already deleted or not found: uploads/missing.pdf
```

## Storage Best Practices

1. **Regular Cleanup**: Run storage stats periodically to identify orphaned files
2. **Monitor Disk Usage**: Check `total_disk_usage_mb` to track storage growth
3. **Cleanup Before Deployment**: Run cleanup to free space before deploying

## Testing

Check current storage status:

```bash
# View stats
curl http://localhost:8000/api/documents/storage/stats

# Cleanup orphaned files
curl -X POST http://localhost:8000/api/documents/storage/cleanup
```

## Implementation Details

### File Deletion

```python
if os.path.exists(file_path):
    os.remove(file_path)
```

### Vector Deletion

```python
vector_store.delete_document(document_id)
# Uses ChromaDB's delete with where filter: {"document_id": doc_id}
```

### Database Deletion

```python
db.delete(db_doc)
db.commit()
# With rollback on error
```

## Error Handling

- **File Not Found**: Logged as warning, doesn't block deletion
- **Vector Store Error**: Logged but doesn't block database deletion
- **Database Error**: Triggers rollback and raises HTTP 500 error

This ensures maximum cleanup even if individual steps fail.
