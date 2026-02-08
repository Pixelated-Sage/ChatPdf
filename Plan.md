AI-powered document chat application that lets users upload multiple PDFs and ask questions across them with citations.
Why Build This:

Portfolio Impact: Showcases full-stack + AI skills (80% of tech job requirements)
Monetization Potential: Freemium SaaS ($10-20/month premium tier)
Client Magnet: Demo this to Oxalate leads → "We can build this for your business docs"
Job Insurance: Every interviewer asks "show me a complex project you built"
Finite Project: 15-20 hours total (4-5 burst sessions)

Business Angle:

B2C: Students pay ₹199/month for unlimited PDFs (target: 100 users = ₹20k/month)
B2B: Companies pay ₹2000/month for team plan (target: 10 companies = ₹20k/month)
Oxalate Lead Gen: "See this AI tool I built? I can customize it for your business."


TARGET USERS & USE CASES
Primary Personas
1. Rohan (Engineering Student)

Problem: Has 15 research papers for project, wastes 2 hours finding specific info
Use: Uploads all papers, asks "What are the main findings on X?"
Pays: ₹199/month (cheaper than buying GPT-4 subscription)

2. Priya (Research Scholar)

Problem: Literature review across 50+ papers, needs citations for thesis
Use: Organizes papers by topic, asks questions, exports answers with sources
Pays: ₹499/month (PhD budget)

3. Startup Founder (B2B)

Problem: Team has 100+ product docs, support tickets, legal docs
Use: Internal knowledge base, all employees can query
Pays: ₹2000/month (team plan)

Secondary (Future)

Legal professionals (case law research)
Healthcare (medical research papers)
Sales teams (product documentation)


COMPETITIVE ANALYSIS
CompetitorPricingLimitationsOur AdvantageChatPDF.comFree: 2 PDFs/day$20/month: UnlimitedSlow, no multi-doc, English onlyFaster (local embeddings), multi-doc queries, Indian pricingHumata.ai$15/month60 pages/file limitNo page limits, better UIAskYourPDF$15/monthGeneric, no customizationCustomizable for B2B clientsGPT-4 File Upload$20/monthOne file at a time, no persistenceMultiple files, organized library
Our Differentiator: Local embeddings (faster) + Gemini Pro (free API) = Lower costs, faster responses, Indian pricing (₹199 vs $15).

TECHNICAL ARCHITECTURE
System Overview
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               FRONTEND (Vercel)                              │
│  • Next.js 14 (App Router) + TypeScript                     │
│  • Tailwind CSS + shadcn/ui                                  │
│  • Zustand (state management)                                │
│  • react-dropzone (file upload)                              │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS (REST + SSE)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (Railway)                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             FastAPI (Async)                           │  │
│  │  • POST /upload (multipart/form-data)                │  │
│  │  • GET /documents (list with metadata)               │  │
│  │  • DELETE /documents/{id}                            │  │
│  │  • POST /chat (SSE streaming)                        │  │
│  │  • GET /conversations                                │  │
│  └─────────┬────────────────────────┬───────────────────┘  │
│            │                        │                       │
│            ▼                        ▼                       │
│  ┌──────────────────┐    ┌──────────────────┐             │
│  │  PDF Processing  │    │   RAG Pipeline   │             │
│  │                  │    │                  │             │
│  │  • PyPDF2        │    │  • Query embed   │             │
│  │  • LangChain     │    │  • Vector search │             │
│  │  • Chunking      │    │  • Rerank        │             │
│  └──────────────────┘    │  • LLM generate  │             │
│                          │  • Stream back   │             │
│                          └──────────────────┘             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              STORAGE LAYER                            │  │
│  │                                                       │  │
│  │  PostgreSQL           ChromaDB         Filesystem    │  │
│  │  ┌──────────┐        ┌────────┐      ┌─────────┐   │  │
│  │  │Documents │        │Vectors │      │ PDFs    │   │  │
│  │  │Metadata  │        │+Chunks │      │ /uploads│   │  │
│  │  ├──────────┤        └────────┘      └─────────┘   │  │
│  │  │Chats     │                                       │  │
│  │  │Messages  │        Gemini Pro API                 │  │
│  │  └──────────┘        (Text Generation)              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
Tech Stack Decisions
Frontend:

Next.js 14 (not 13) - App Router, React Server Components
TypeScript - Type safety (prevents bugs in production)
Tailwind + shadcn/ui - Fast UI development, professional look
Zustand - Simple state (documents, chat history)
Deployment: Vercel (free tier, auto-deploy on push)

Backend:

FastAPI (not Django) - Async, fast, perfect for streaming
Python 3.11+ - Latest stable
Pydantic v2 - Validation
SQLAlchemy 2.0 - Database ORM
Deployment: Railway (free tier, PostgreSQL included)

AI/ML:

sentence-transformers (all-MiniLM-L6-v2) - Local embeddings, 384 dims, fast
ChromaDB - Vector storage, embedded mode
Gemini Pro - Free till April 2026, streaming support
LangChain - Text chunking (RecursiveCharacterTextSplitter)

Database:

PostgreSQL - Metadata (Railway managed, free tier)
ChromaDB - Vector embeddings (runs in backend process)
Filesystem - PDF storage (Railway persistent disk)

Why These Choices:

Free Tier Everything - Vercel + Railway + Gemini = ₹0 hosting
Fast Development - Familiar stack, lots of examples
Scalable - Can handle 100-1000 users without changes
Portfolio Ready - Modern stack employers look for


DATABASE SCHEMA
PostgreSQL Tables
sql-- Users (Phase 2 - auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan VARCHAR(20) DEFAULT 'free', -- free, premium, enterprise
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,      -- bytes
    page_count INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,    -- for tracking
    upload_date TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT NULL
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),              -- auto-generated from first question
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations JSONB NULL,            -- [{doc_id, filename, page, chunk_text}, ...]
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversation-Document mapping (many-to-many)
CREATE TABLE conversation_documents (
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (conversation_id, document_id)
);

-- Indexes for performance
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
ChromaDB Collection Structure
python{
    "collection_name": "document_chunks",
    "metadata": {"description": "All document embeddings"},
    
    "documents": {
        "ids": ["doc_uuid_chunk_0", "doc_uuid_chunk_1", ...],
        "embeddings": [[0.123, -0.456, ...], ...],  # 384-dim vectors
        "metadatas": [
            {
                "document_id": "uuid",
                "user_id": "uuid",           # For multi-user filtering
                "filename": "research.pdf",
                "page": 5,
                "chunk_index": 0,
                "chunk_length": 487,
                "chunk_text": "First 100 chars preview..."
            },
            ...
        ],
        "documents": ["Full chunk text here...", ...]
    }
}
```

---

## API SPECIFICATION

### Base URL
- **Development:** `http://localhost:8000`
- **Production:** `https://chatpdf-api.railway.app`

### Authentication (Phase 2)
```
Authorization: Bearer <jwt_token>
Endpoints
1. Upload Document
httpPOST /api/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
{
  "file": <PDF binary>
}

Response 202 Accepted:
{
  "document_id": "uuid",
  "filename": "research.pdf",
  "status": "processing",
  "message": "Document queued for processing"
}

Response 400 Bad Request:
{
  "detail": "File size exceeds 10MB limit"
}

Response 422 Unprocessable Entity:
{
  "detail": "File must be a PDF"
}
Processing Flow:

Validate file (type, size)
Save to /uploads/{user_id}/{uuid}.pdf
Queue background task (extract text, chunk, embed, store)
Return 202 immediately
Frontend polls /api/documents/{id} for status


2. Get Upload Status
httpGET /api/documents/{document_id}
Authorization: Bearer <token>

Response 200 OK:
{
  "id": "uuid",
  "filename": "research.pdf",
  "status": "processing",  // or "ready", "failed"
  "progress": 65,           // 0-100
  "page_count": 15,
  "chunk_count": 45,
  "error": null
}

3. List Documents
httpGET /api/documents
Authorization: Bearer <token>
Query Params:
  - sort_by: name | date | size (default: date)
  - order: asc | desc (default: desc)

Response 200 OK:
{
  "documents": [
    {
      "id": "uuid",
      "filename": "research.pdf",
      "file_size": 2048000,    // bytes
      "page_count": 15,
      "chunk_count": 45,
      "upload_date": "2026-01-28T14:30:00Z",
      "status": "ready"
    },
    ...
  ],
  "total": 5
}

4. Delete Document
httpDELETE /api/documents/{document_id}
Authorization: Bearer <token>

Response 200 OK:
{
  "message": "Document deleted successfully",
  "document_id": "uuid"
}
Cleanup:

Delete from PostgreSQL (cascades to messages)
Delete vectors from ChromaDB
Delete PDF file from filesystem


5. Chat (Ask Question)
httpPOST /api/chat
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "question": "What are the main findings about quantum computing?",
  "conversation_id": "uuid",        // optional, creates new if null
  "document_ids": ["uuid1", "uuid2"]  // optional, uses all if null
}

Response 200 OK (Server-Sent Events):
Content-Type: text/event-stream

data: {"type": "start", "conversation_id": "uuid"}

data: {"type": "chunk", "content": "The main findings"}

data: {"type": "chunk", "content": " about quantum"}

data: {"type": "chunk", "content": " computing are..."}

data: {"type": "citation", "data": {"document_id": "uuid", "filename": "research.pdf", "page": 5, "chunk_text": "Our experiments show..."}}

data: {"type": "done", "message_id": "uuid"}
RAG Pipeline:

Embed question (sentence-transformers)
Query ChromaDB (top 5 similar chunks, filter by user_id + doc_ids)
Rerank chunks (optional, using cross-encoder)
Build context prompt for Gemini
Stream response from Gemini
Parse citations from response
Save conversation to PostgreSQL


6. Get Conversation
httpGET /api/conversations/{conversation_id}
Authorization: Bearer <token>

Response 200 OK:
{
  "id": "uuid",
  "title": "Quantum Computing Research",
  "created_at": "2026-01-28T14:00:00Z",
  "updated_at": "2026-01-28T14:35:00Z",
  "messages": [
    {
      "role": "user",
      "content": "What are the main findings?",
      "created_at": "2026-01-28T14:30:00Z"
    },
    {
      "role": "assistant",
      "content": "The main findings are...",
      "citations": [
        {
          "document_id": "uuid",
          "filename": "research.pdf",
          "page": 5,
          "chunk_text": "Our results show..."
        }
      ],
      "created_at": "2026-01-28T14:30:05Z"
    }
  ],
  "documents": [
    {
      "id": "uuid",
      "filename": "research.pdf",
      "page_count": 15
    }
  ]
}

7. List Conversations
httpGET /api/conversations
Authorization: Bearer <token>

Response 200 OK:
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Quantum Computing Research",
      "message_count": 8,
      "document_count": 3,
      "updated_at": "2026-01-28T14:35:00Z"
    },
    ...
  ],
  "total": 12
}
```

---

## PROJECT PHASES (Burst Sprints)

### Phase 1: Backend Foundation (4-5 hours)

**Goal:** Working API that can upload PDFs and extract text

**Tasks:**
- [x] Project setup (FastAPI structure)
- [x] PDF upload endpoint
- [x] Text extraction (PyPDF2)
- [x] Database models (SQLAlchemy)
- [x] Basic error handling
- [x] Test with Postman/curl

**Deliverables:**
- FastAPI app running on `localhost:8000`
- `/upload` endpoint accepts PDF
- Extracted text stored
- `/docs` shows API documentation

**Agent Assignment:**
```
@backend: Create FastAPI project structure with:
- app/main.py (FastAPI app, CORS)
- app/models.py (SQLAlchemy models)
- app/schemas.py (Pydantic models)
- app/routes/upload.py (upload endpoint)
- app/services/pdf_processor.py (text extraction)

Use Abhishek's Arch environment (venv at /data/venvs/chatpdf-backend)
Success Criteria:
bash# Upload PDF
curl -X POST http://localhost:8000/upload \
  -F "file=@sample.pdf"

# Response
{"document_id": "uuid", "status": "processing"}
```

---

### Phase 2: RAG Pipeline (5-6 hours)

**Goal:** Question answering with citations working

**Tasks:**
- [ ] Text chunking (LangChain)
- [ ] Embedding generation (sentence-transformers)
- [ ] ChromaDB integration
- [ ] Gemini Pro API setup
- [ ] Chat endpoint (streaming)
- [ ] Citation parsing

**Deliverables:**
- Upload PDF → Auto-chunks → Embeds → Stores in ChromaDB
- Ask question → Returns streaming answer with citations

**Agent Assignment:**
```
@ml: Implement RAG pipeline:
1. Text chunking in app/services/pdf_processor.py
   - LangChain RecursiveCharacterTextSplitter
   - 500 token chunks, 50 token overlap
   
2. Embedding generation in app/services/embeddings.py
   - sentence-transformers 'all-MiniLM-L6-v2'
   - Batch processing for speed
   - Cache model in /data/models/embeddings/
   
3. ChromaDB integration in app/services/vector_store.py
   - Store embeddings with metadata
   - Query by similarity

@backend: Implement chat endpoint:
- app/routes/chat.py
- Streaming with Server-Sent Events
- Integrate with RAG pipeline
- Parse citations from Gemini response
Success Criteria:
bash# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "document_ids": ["uuid"]}'

# Response (SSE)
data: {"type": "chunk", "content": "The main topic..."}
data: {"type": "citation", "data": {"page": 3, "filename": "research.pdf"}}
data: {"type": "done"}
```

---

### Phase 3: Frontend (5-6 hours)

**Goal:** Beautiful UI for uploading and chatting

**Tasks:**
- [ ] Next.js project setup
- [ ] File upload component (drag-drop)
- [ ] Document list sidebar
- [ ] Chat interface (streaming text)
- [ ] Citation popovers
- [ ] Responsive design

**Deliverables:**
- Clean, ChatGPT-like interface
- Works on mobile
- Real-time streaming responses
- Citations clickable

**Agent Assignment:**
```
@frontend: Build Next.js app:

1. Upload page (app/upload/page.tsx)
   - react-dropzone for drag-drop
   - Progress indicator
   - File validation

2. Chat page (app/chat/page.tsx)
   - Message list (user + AI)
   - Streaming text display
   - Input box with character counter

3. Components:
   - components/DocumentSidebar.tsx
   - components/ChatMessage.tsx
   - components/CitationPopover.tsx

Stack detected: Next.js 14 + Tailwind + shadcn/ui
Mobile-first, dark mode support
```

**Success Criteria:**
- Upload PDF via drag-drop
- See processing progress
- Ask question, see streaming response
- Click citation, see source snippet

---

### Phase 4: Polish & Deploy (2-3 hours)

**Goal:** Production-ready app

**Tasks:**
- [ ] Error handling (all edge cases)
- [ ] Loading states (skeletons)
- [ ] Empty states (no documents yet)
- [ ] Toast notifications
- [ ] README documentation
- [ ] Deploy to Vercel + Railway

**Agent Assignment:**
```
@qa: Security audit:
- Check for hardcoded secrets
- Test file upload limits
- SQL injection tests
- CORS configuration

@devops: Deploy:
- Backend to Railway
- Frontend to Vercel
- Set environment variables
- Test production deployment

@frontend: Polish UI:
- Loading skeletons
- Error boundaries
- Toast notifications
- Empty states
Success Criteria:

App live at chatpdf.vercel.app
API at chatpdf-api.railway.app
No errors in production
Beautiful UX


CRITICAL IMPLEMENTATION DETAILS
1. Smart Chunking Strategy
Problem: Naive chunking (every 500 chars) breaks sentences, loses context.
Solution:
pythonfrom langchain.text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,           # ~400 words
    chunk_overlap=50,         # Preserve context across chunks
    separators=[
        "\n\n",              # Paragraph breaks first
        "\n",                # Line breaks second
        ". ",                # Sentences third
        " ",                 # Words last resort
        ""
    ],
    length_function=len
)

chunks = splitter.split_text(extracted_text)
Metadata to Store:
python{
    "document_id": "uuid",
    "page": 5,               # Which page this came from
    "chunk_index": 2,        # Order in document
    "chunk_text": "...",     # Full text
    "preview": "First 100 chars..."  # For citation display
}

2. Embedding Generation (Optimized)
Model: sentence-transformers/all-MiniLM-L6-v2

Size: 80MB (small enough for Railway)
Dims: 384 (fast similarity search)
Speed: ~1000 chunks/second on CPU

Code:
pythonfrom sentence_transformers import SentenceTransformer
from pathlib import Path

# CRITICAL: Load model once, reuse
MODEL_PATH = Path("/data/models/embeddings/all-MiniLM-L6-v2")

if not MODEL_PATH.exists():
    # First time: Download to /data
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save(str(MODEL_PATH))
else:
    # Load from /data (respects partition structure)
    model = SentenceTransformer(str(MODEL_PATH))

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Batch embed for speed"""
    embeddings = model.encode(
        chunks,
        batch_size=32,       # Balance speed vs memory
        show_progress_bar=True
    )
    return embeddings.tolist()

3. ChromaDB Setup
Storage: Persistent mode (survives restarts)
pythonimport chromadb
from chromadb.config import Settings

# For development (local)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/data/chroma_db"  # Abhishek's /data partition
))

# For production (Railway)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/app/chroma_db"   # Railway persistent disk
))

collection = client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)

# Add embeddings
collection.add(
    ids=["doc_uuid_chunk_0", "doc_uuid_chunk_1", ...],
    embeddings=[[0.1, 0.2, ...], ...],
    metadatas=[{"document_id": "...", "page": 5}, ...],
    documents=["chunk text...", ...]
)

# Query
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],  # User question embedding
    n_results=5,
    where={"document_id": {"$in": ["uuid1", "uuid2"]}}  # Filter by docs
)

4. Gemini Pro Integration (Streaming)
Setup:
pythonimport google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def generate_answer(question: str, context_chunks: List[dict]):
    # Build context
    context = "\n\n".join([
        f"[Source: {c['filename']}, Page {c['page']}]\n{c['text']}"
        for c in context_chunks
    ])
    
    prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Instructions:
- Be concise but complete
- Cite sources using [Filename, Page X] format
- If multiple sources support a point, cite all

Answer:"""
    
    # Stream response
    response = model.generate_content(prompt, stream=True)
    
    for chunk in response:
        if chunk.text:
            yield chunk.text
Streaming Endpoint (FastAPI):
pythonfrom fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        # Embed question
        question_embedding = embed_text(request.question)
        
        # Query ChromaDB
        results = query_vector_store(question_embedding, request.document_ids)
        
        # Stream from Gemini
        for chunk in generate_answer(request.question, results):
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
```

---

### 5. Citation Parsing

**Gemini Response:**
```
The main findings are X and Y [research.pdf, Page 3]. Additionally, Z was observed [textbook.pdf, Page 12].
Parse Citations:
pythonimport re

def parse_citations(text: str, chunks: List[dict]) -> List[dict]:
    """Extract [Filename, Page X] citations"""
    pattern = r'\[([^,]+),\s*Page\s*(\d+)\]'
    citations = []
    
    for match in re.finditer(pattern, text):
        filename = match.group(1).strip()
        page = int(match.group(2))
        
        # Find matching chunk
        for chunk in chunks:
            if chunk['filename'] == filename and chunk['page'] == page:
                citations.append({
                    'document_id': chunk['document_id'],
                    'filename': filename,
                    'page': page,
                    'chunk_text': chunk['text'][:200]  # Preview
                })
                break
    
    return citations

6. Frontend Streaming Display
React Component:
tsx'use client';

import { useState } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);

  const sendMessage = async (question: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    
    // Start streaming
    setStreaming(true);
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    
    let aiMessage = { role: 'assistant', content: '', citations: [] };
    setMessages(prev => [...prev, aiMessage]);
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'chunk') {
            // Append text to AI message
            setMessages(prev => {
              const updated = [...prev];
              updated[updated.length - 1].content += data.content;
              return updated;
            });
          } else if (data.type === 'citation') {
            // Add citation
            setMessages(prev => {
              const updated = [...prev];
              updated[updated.length - 1].citations.push(data.data);
              return updated;
            });
          }
        }
      }
    }
    
    setStreaming(false);
  };
  
  return (
    <div className="flex flex-col h-screen">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
      </div>
      
      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={streaming} />
    </div>
  );
}

MONETIZATION STRATEGY
Pricing Tiers
TierPrice (INR)Price (USD)FeaturesTargetFree₹0$02 PDFs/day, 10 questions/dayTrial usersStudent₹199/month$2.49/month50 PDFs, unlimited questionsStudentsProfessional₹499/month$6/monthUnlimited PDFs, priority supportResearchersTeam₹2000/month$25/month10 users, shared workspaceStartups
Revenue Projections
Conservative (3 months):

50 Student users × ₹199 = ₹9,950/month
5 Professional users × ₹499 = ₹2,495/month
Total: ₹12,445/month

Target (6 months):

100 Student users × ₹199 = ₹19,900/month
10 Professional users × ₹499 = ₹4,990/month
2 Team plans × ₹2000 = ₹4,000/month
Total: ₹28,890/month

Optimistic (12 months):

200 Student users = ₹39,800
20 Professional users = ₹9,980
5 Team plans = ₹10,000
Total: ₹59,780/month

Marketing Channels

Reddit - r/Indian_Academia, r/IndianStudents

Post: "Built a ChatGPT for PDFs with Indian pricing"
Cost: Free


Twitter/X - Tech community

Demo video
Tag: #IndieHackers, #BuildInPublic


College WhatsApp Groups

Vaibhav's network
Offer: First 50 users → ₹99/month lifetime


Oxalate Portfolio

"See this AI tool? We build custom versions for businesses"
B2B lead generator


SEO - Target keywords

"ChatPDF alternative India"
"PDF chat AI free"
"Ask questions to PDF"




SUCCESS METRICS
Technical Metrics

 Upload processing: <30 seconds per 10MB PDF
 Query response time: First chunk in <2 seconds
 Citation accuracy: >90% (manual spot-check)
 Uptime: >95%
 Error rate: <1% of requests

Business Metrics

 Week 1: App deployed and live
 Week 2: First 10 sign-ups
 Week 4: First paying customer
 Week 8: ₹5,000/month MRR
 Week 12: ₹20,000/month MRR

Portfolio Metrics

 GitHub stars: 50+ (shows interest)
 Demo video views: 500+
 Resume clicks: Use in job applications
 Oxalate leads: Show in 5+ sales calls


RISK MITIGATION
Technical Risks
RiskImpactMitigationGemini API failsHIGHFallback to OpenAI API (pay per use)Railway free tier limitsMEDIUMOptimize queries, add cachingChromaDB too slowMEDIUMUse Pinecone (managed, faster)PDF extraction failsLOWRobust error handling, retry logic
Business Risks
RiskImpactMitigationNo users sign upHIGHFree tier + aggressive marketingUsers don't upgradeMEDIUMFeature gates (5 PDFs free, then paywall)Competition launchesLOWMove fast, differentiate on Indian pricingGemini API becomes paidMEDIUMAlready profitable by then, can pay