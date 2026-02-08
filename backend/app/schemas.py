from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    page_count: int

class DocumentCreate(DocumentBase):
    file_path: str

class Document(DocumentBase):
    id: str
    upload_date: datetime
    processed: bool
    processing_error: Optional[str] = None
    chunk_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    role: str
    content: str
    citations: Optional[List[dict]] = None

class MessageCreate(MessageBase):
    conversation_id: str

class Message(MessageBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    document_ids: Optional[List[str]] = None

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
