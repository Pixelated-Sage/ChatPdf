from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.chat_service import chat_service
import json
import asyncio
import uuid

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    # 1. Handle Conversation
    conv_id = request.conversation_id
    if not conv_id:
        conv_id = str(uuid.uuid4())
        # Auto-generate title using AI
        title = chat_service.generate_title(request.question)
        db_conv = models.Conversation(id=conv_id, title=title)
        db.add(db_conv)
        db.commit()

    else:
        db_conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
        if not db_conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Save User Message
    user_msg = models.Message(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        role="user",
        content=request.question
    )
    db.add(user_msg)
    db.commit()

    async def event_stream():
        full_content = ""
        citations = []
        try:
            # Yield start event
            yield f"data: {json.dumps({'type': 'start', 'conversation_id': conv_id})}\n\n"

            async for part in chat_service.generate_answer(
                question=request.question,
                doc_ids=request.document_ids
            ):
                if part["type"] == "done":
                    full_content = part.get("full_content", "")
                    citations = part.get("citations", [])
                
                yield f"data: {json.dumps(part)}\n\n"
                # await asyncio.sleep(0.01) # No longer needed with real async stream

            # 3. Save Assistant Message
            if full_content:
                assistant_msg = models.Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conv_id,
                    role="assistant",
                    content=full_content,
                    citations=citations
                )
                # We need a new session or be careful with the current one in async generator
                # Usually best to use a fresh session for the background save if needed,
                # but here we can just use the provided db if it stays alive.
                # Since StreamingResponse keeps the request alive, it should be fine.
                db.add(assistant_msg)
                
                # Update conversation timestamp
                db_conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
                if db_conv:
                    from datetime import datetime
                    db_conv.updated_at = datetime.utcnow()
                
                db.commit()

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
