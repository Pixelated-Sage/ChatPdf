from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["conversations"])

@router.get("/conversations", response_model=List[schemas.Conversation])
async def list_conversations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    conversations = db.query(models.Conversation).order_by(models.Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    return conversations

@router.get("/conversations/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # We might want to include messages in a more detailed schema
    return db_conv

@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.Message])
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
    return messages

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(db_conv)
    db.commit()
    
    return {"message": "Conversation deleted successfully", "conversation_id": conversation_id}
@router.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
    
    export_text = f"# {db_conv.title or 'ChatPDF Conversation'}\n\n"
    export_text += f"ID: {db_conv.id}\n"
    export_text += f"Created: {db_conv.created_at}\n\n---\n\n"
    
    for msg in messages:
        role = "User" if msg.role == "user" else "Assistant"
        export_text += f"### {role}\n{msg.content}\n\n"
        if msg.citations:
            export_text += "**Citations:**\n"
            for cite in msg.citations:
                export_text += f"- {cite['filename']}, Page {cite['page']}\n"
            export_text += "\n"
        export_text += "---\n\n"
        
    return {
        "filename": f"conversation_{conversation_id[:8]}.md",
        "content": export_text
    }

@router.patch("/conversations/{conversation_id}/rename", response_model=schemas.Conversation)
async def rename_conversation(conversation_id: str, request: schemas.ConversationBase, db: Session = Depends(get_db)):
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if request.title:
        db_conv.title = request.title
        db.commit()
        db.refresh(db_conv)
    
    return db_conv
