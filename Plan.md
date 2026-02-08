**STOP. Let me restructure this for REALITY.**

Your doc is 90% perfect but has **one fatal flaw**: Ollama won't run on Railway free tier (needs 2-4GB RAM, Railway gives 512MB).

Let me give you the **ACTUAL deployable architecture** + Antigravity-ready product doc.

---

# ChatPDF v2 - Product Specification (Antigravity-Ready)

## EXECUTIVE SUMMARY

**What:** RAG-based PDF chat app (upload PDFs, ask questions, get cited answers)  
**Why:** Portfolio showcase + potential ₹20k/month SaaS  
**How:** Next.js + FastAPI + sentence-transformers + Gemini Pro API  
**Timeline:** 15-20 hours (4 burst sessions)  
**Cost:** ₹0/month (all free tiers)

---

## ARCHITECTURE (Reality-Checked for Free Tier Deployment)

```
┌─────────────────────────────────────────────────────────┐
│                  USER (Browser)                         │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│         FRONTEND (Vercel - Free Tier)                   │
│  • Next.js 14 + TypeScript                              │
│  • Tailwind + shadcn/ui                                 │
│  • Server-Sent Events (SSE) for streaming               │
└────────────────┬───────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────┐
│         BACKEND (Railway - Free Tier)                   │
│  ┌────────────────────────────────────────────────┐    │
│  │  FastAPI (Python 3.11)                         │    │
│  │  • POST /upload (PDF processing)               │    │
│  │  • GET /documents (list PDFs)                  │    │
│  │  • POST /chat (streaming answers)              │    │
│  │  • DELETE /documents/{id}                      │    │
│  └──────────┬─────────────────┬───────────────────┘    │
│             │                 │                         │
│             ▼                 ▼                         │
│  ┌──────────────────┐  ┌─────────────────┐            │
│  │ PDF Processing   │  │  RAG Pipeline   │            │
│  │ • PyPDF2         │  │  • Embed query  │            │
│  │ • Text extract   │  │  • Vector search│            │
│  │ • Chunking       │  │  • Generate ans │            │
│  └──────────────────┘  └─────────────────┘            │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │           STORAGE (All on Railway)             │   │
│  │                                                 │   │
│  │  SQLite                ChromaDB     Filesystem │   │
│  │  ┌──────────┐        ┌────────┐   ┌────────┐ │   │
│  │  │Metadata  │        │Vectors │   │ PDFs   │ │   │
│  │  │Documents │        │Embeddin│   │ /upload│ │   │
│  │  │Chats     │        │gs      │   │        │ │   │
│  │  └──────────┘        └────────┘   └────────┘ │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  External API (NOT running on Railway):                │
│  ┌────────────────────────────────────────────────┐   │
│  │  Gemini Pro API (Google, Free till April 2026)│   │
│  │  • Text generation                             │   │
│  │  • Streaming support                           │   │
│  │  • 60 requests/minute free tier                │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## CRITICAL TECH STACK DECISIONS

### ✅ What WORKS on Railway Free Tier (512MB RAM)

| Component | Solution | Why |
|-----------|----------|-----|
| **Embeddings** | `sentence-transformers` (all-MiniLM-L6-v2) | 80MB model, runs on CPU, 384-dim vectors |
| **Vector Store** | ChromaDB (embedded mode) | No separate server needed, stores in SQLite |
| **Database** | SQLite | Railway includes it, no setup needed |
| **LLM** | **Gemini Pro API** | Free till April 2026, streaming, 1M tokens/day limit |
| **PDF Storage** | Railway filesystem | 1GB persistent storage |

### ❌ What DOESN'T WORK on Railway Free Tier

| Component | Why It Fails | Alternative |
|-----------|--------------|-------------|
| **Ollama** | Needs 2-4GB RAM minimum | Use Gemini Pro API instead |
| **PostgreSQL** | Railway charges for DB | Use SQLite (included free) |
| **Large Models** | 7B models need 4-8GB RAM | Stick to sentence-transformers |

### 🔄 Fallback Strategy (If Gemini API Expires)

```python
# Primary: Gemini Pro (free till April 2026)
if GEMINI_API_KEY:
    llm = GeminiPro()

# Fallback 1: OpenAI (pay $0.002 per 1K tokens)
elif OPENAI_API_KEY:
    llm = OpenAI(model="gpt-3.5-turbo")

# Fallback 2: Groq (free, fast, 6K tokens/min)
elif GROQ_API_KEY:
    llm = Groq(model="llama3-8b")
```

---

## DATABASE SCHEMA (SQLite - Simplified)

```sql
-- documents table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,              -- UUID
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,          -- /uploads/{id}.pdf
    file_size INTEGER,                -- bytes
    page_count INTEGER,
    chunk_count INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'processing'  -- processing, ready, failed
);

-- conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,                       -- Auto-generated from first question
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id),
    role TEXT CHECK(role IN ('user', 'assistant')),
    content TEXT,
    citations TEXT,                   -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- conversation_documents (many-to-many)
CREATE TABLE conversation_documents (
    conversation_id TEXT REFERENCES conversations(id),
    document_id TEXT REFERENCES documents(id),
    PRIMARY KEY (conversation_id, document_id)
);
```

**ChromaDB Collection:**
```python
{
    "collection_name": "pdf_chunks",
    "documents": {
        "ids": ["doc1_chunk_0", "doc1_chunk_1", ...],
        "embeddings": [[0.123, -0.456, ...], ...],  # 384-dim
        "metadatas": [
            {
                "document_id": "doc1",
                "filename": "research.pdf",
                "page": 5,
                "chunk_index": 0
            }
        ],
        "documents": ["Full chunk text..."]
    }
}
```

---

## API ENDPOINTS

### 1. Upload PDF
```http
POST /api/upload
Content-Type: multipart/form-data

Body: { "file": <PDF binary> }

Response 200:
{
  "document_id": "uuid",
  "filename": "research.pdf",
  "status": "processing"
}
```

### 2. List Documents
```http
GET /api/documents

Response 200:
{
  "documents": [
    {
      "id": "uuid",
      "filename": "research.pdf",
      "page_count": 15,
      "chunk_count": 45,
      "uploaded_at": "2026-02-08T10:30:00Z",
      "status": "ready"
    }
  ]
}
```

### 3. Chat (Streaming)
```http
POST /api/chat
Content-Type: application/json

Body:
{
  "question": "What are the main findings?",
  "document_ids": ["uuid1", "uuid2"]  # optional
}

Response (Server-Sent Events):
data: {"type": "chunk", "content": "The main findings"}
data: {"type": "chunk", "content": " are..."}
data: {"type": "citation", "data": {"filename": "research.pdf", "page": 5}}
data: {"type": "done"}
```

### 4. Delete Document
```http
DELETE /api/documents/{id}

Response 200:
{
  "message": "Document deleted"
}
```

---

## 4-PHASE BUILD PLAN (Antigravity Execution)

### **Phase 1: Backend Foundation** (5 hours)

**Agent:** `@backend` + `@devops`

**Deliverables:**
- FastAPI app structure
- PDF upload endpoint
- Text extraction (PyPDF2)
- SQLite database setup
- File storage on Railway

**Code Structure:**
```
chatpdf-backend/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── database.py          # SQLite connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response
│   ├── routes/
│   │   ├── upload.py        # POST /upload
│   │   ├── documents.py     # GET /documents, DELETE /documents/{id}
│   │   └── chat.py          # POST /chat (placeholder)
│   └── services/
│       └── pdf_processor.py # PyPDF2 text extraction
├── uploads/                 # PDF storage
├── chroma_db/              # ChromaDB persistence
├── requirements.txt
└── .env.example
```

**Success Criteria:**
```bash
# Upload PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.pdf"

# Response
{"document_id": "abc123", "filename": "test.pdf", "status": "processing"}

# List documents
curl http://localhost:8000/api/documents

# Response
{"documents": [{"id": "abc123", "filename": "test.pdf", "status": "ready"}]}
```

**Antigravity Command:**
```
@backend create FastAPI project:
- Project name: chatpdf-backend
- Python 3.11
- Use /data/venvs/chatpdf-backend for venv
- Code in ~/Documents/C02/chatpdf-backend
- Install: fastapi, uvicorn, sqlalchemy, pypdf2, python-multipart
- Setup SQLite database in app/database.py
- Create upload endpoint with file validation (PDF only, max 10MB)
- Store PDFs in /uploads/{uuid}.pdf
- Extract text and save metadata to documents table

@devops create Railway deployment config:
- Create Procfile: web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
- Create railway.toml with persistent storage
- Set environment variables template
```

---

### **Phase 2: RAG Pipeline** (6 hours)

**Agent:** `@ml` + `@backend`

**Deliverables:**
- Text chunking (LangChain)
- Embedding generation (sentence-transformers)
- ChromaDB integration
- Gemini Pro API integration
- Streaming chat endpoint

**New Files:**
```
app/services/
├── embeddings.py        # sentence-transformers wrapper
├── vector_store.py      # ChromaDB operations
├── chunking.py          # LangChain text splitter
└── llm.py               # Gemini Pro API client
```

**RAG Flow:**
```python
# 1. User uploads PDF
→ Extract text (PyPDF2)
→ Split into chunks (LangChain, 500 chars, 50 overlap)
→ Generate embeddings (sentence-transformers)
→ Store in ChromaDB with metadata

# 2. User asks question
→ Embed question (same model)
→ Query ChromaDB (top 5 similar chunks)
→ Build context prompt
→ Stream answer from Gemini Pro
→ Parse citations
→ Save to messages table
```

**Success Criteria:**
```bash
# Upload PDF (auto-processes)
curl -X POST http://localhost:8000/api/upload -F "file=@research.pdf"
# Wait 10-30 seconds for processing

# Ask question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'

# Response (streaming)
data: {"type": "chunk", "content": "The main topic is..."}
data: {"type": "citation", "data": {"filename": "research.pdf", "page": 3}}
data: {"type": "done"}
```

**Antigravity Command:**
```
@ml implement RAG pipeline:

1. Install: sentence-transformers, chromadb, langchain, google-generativeai

2. Create app/services/embeddings.py:
   - Load 'all-MiniLM-L6-v2' model
   - Cache model in /data/models/embeddings/
   - Function: embed_text(text: str) -> List[float]
   - Function: embed_batch(texts: List[str]) -> List[List[float]]

3. Create app/services/chunking.py:
   - Use RecursiveCharacterTextSplitter
   - chunk_size=500, chunk_overlap=50
   - Preserve paragraph/sentence boundaries

4. Create app/services/vector_store.py:
   - ChromaDB client with persist_directory="./chroma_db"
   - add_document(doc_id, chunks, embeddings, metadatas)
   - query(question_embedding, document_ids, top_k=5)
   - delete_document(doc_id)

5. Create app/services/llm.py:
   - Gemini Pro client (use GEMINI_API_KEY env var)
   - generate_answer(question, context_chunks, stream=True)
   - Return generator that yields text chunks

@backend update routes/upload.py:
- After PDF upload, trigger background task:
  1. Extract text
  2. Chunk text
  3. Generate embeddings
  4. Store in ChromaDB
  5. Update document status to "ready"

@backend implement routes/chat.py:
- POST /chat endpoint
- Streaming response with Server-Sent Events
- Flow:
  1. Embed user question
  2. Query ChromaDB
  3. Build prompt with context
  4. Stream from Gemini Pro
  5. Parse citations
  6. Save conversation
```

---

### **Phase 3: Frontend** (5 hours)

**Agent:** `@frontend`

**Deliverables:**
- Next.js 14 app with App Router
- File upload with drag-drop
- Document list sidebar
- Streaming chat interface
- Citation display

**Page Structure:**
```
chatpdf-frontend/
├── app/
│   ├── layout.tsx           # Root layout, dark mode
│   ├── page.tsx             # Home (redirect to /chat)
│   ├── upload/
│   │   └── page.tsx         # Upload page
│   └── chat/
│       └── page.tsx         # Chat interface
├── components/
│   ├── FileUpload.tsx       # Drag-drop upload
│   ├── DocumentSidebar.tsx  # List of PDFs
│   ├── ChatMessage.tsx      # Single message bubble
│   ├── ChatInput.tsx        # Question input box
│   └── CitationBadge.tsx    # Clickable citation
└── lib/
    ├── api.ts               # Backend API client
    └── types.ts             # TypeScript types
```

**UI Components (shadcn/ui):**
- Button, Card, Input, Textarea
- Badge (for citations)
- Dialog (for citation preview)
- Toast (for notifications)
- Skeleton (loading states)

**Success Criteria:**
- Drag-drop PDF → see upload progress
- Click uploaded PDF → opens chat
- Type question → see streaming answer
- Click citation → see source text popup

**Antigravity Command:**
```
@frontend create Next.js app:

1. Setup:
   - Next.js 14 with App Router
   - TypeScript strict mode
   - Tailwind CSS + shadcn/ui
   - Code in ~/Documents/C02/chatpdf-frontend
   - API base URL: http://localhost:8000 (dev), env var for prod

2. Create app/upload/page.tsx:
   - react-dropzone for drag-drop
   - File validation (PDF only, max 10MB)
   - Upload progress bar
   - Success: redirect to /chat
   - Error: toast notification

3. Create app/chat/page.tsx:
   - Layout: DocumentSidebar (left) + Chat (right)
   - Mobile: tabs to switch between sidebar and chat
   - Fetch documents on mount
   - Click document → load conversation or start new

4. Create components/ChatMessage.tsx:
   - User messages: right-aligned, blue background
   - AI messages: left-aligned, gray background
   - Citations: inline badges [research.pdf, p.5]
   - Click citation → dialog with full chunk text

5. Create components/ChatInput.tsx:
   - Textarea with auto-expand
   - Send button (disabled while streaming)
   - Character counter (max 500 chars)

6. Implement streaming:
   - Use EventSource for Server-Sent Events
   - Append chunks to AI message in real-time
   - Handle citations and done events

7. Polish:
   - Dark mode support
   - Loading skeletons
   - Empty states ("No documents yet")
   - Error boundaries
```

---

### **Phase 4: Deploy & Polish** (3 hours)

**Agent:** `@devops` + `@qa` + `@frontend`

**Deliverables:**
- Backend deployed to Railway
- Frontend deployed to Vercel
- Environment variables configured
- Error handling tested
- README documentation

**Deployment Checklist:**
- [ ] Backend: Railway deployment successful
- [ ] Frontend: Vercel deployment successful
- [ ] CORS configured (allow frontend domain)
- [ ] Environment variables set (GEMINI_API_KEY)
- [ ] Persistent storage enabled on Railway
- [ ] Custom domain configured (chatpdf.abhishek.oxalate.com)
- [ ] SSL certificates active
- [ ] Uptime monitoring enabled

**Success Criteria:**
```bash
# Production URLs work
curl https://chatpdf-api.railway.app/api/documents
curl https://chatpdf.vercel.app

# Upload + chat flow works end-to-end
# No console errors
# Mobile responsive
# Streams properly
```

**Antigravity Command:**
```
@devops deploy backend to Railway:
1. Create new Railway project
2. Connect GitHub repo (chatpdf-backend)
3. Set environment variables:
   - GEMINI_API_KEY=...
   - DATABASE_URL=sqlite:///./app.db
4. Configure persistent storage for /uploads and /chroma_db
5. Deploy and test /health endpoint

@devops deploy frontend to Vercel:
1. Create new Vercel project
2. Connect GitHub repo (chatpdf-frontend)
3. Set environment variables:
   - NEXT_PUBLIC_API_URL=https://chatpdf-api.railway.app
4. Deploy and test

@frontend add final polish:
- Toast notifications for errors
- Loading skeletons everywhere
- Empty states with helpful text
- 404 page
- Add meta tags for SEO

@qa security audit:
- Check for hardcoded secrets (NONE allowed)
- Test file upload limits (should reject >10MB)
- Test malicious file uploads (non-PDF should fail)
- Test CORS (only frontend domain allowed)
- Test rate limiting (if needed)

@backend create comprehensive README:
- Architecture diagram
- Setup instructions (local + deployment)
- API documentation
- Environment variables reference
- Troubleshooting guide
```

---

## ENVIRONMENT VARIABLES

### Backend (.env)
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults work)
DATABASE_URL=sqlite:///./app.db
UPLOAD_DIR=./uploads
CHROMA_DIR=./chroma_db
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_ORIGINS=http://localhost:3000,https://chatpdf.vercel.app
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000        # dev
NEXT_PUBLIC_API_URL=https://chatpdf-api.railway.app  # prod
```

---

## SUCCESS METRICS

**Technical:**
- ✅ Upload 10MB PDF → processed in <30 seconds
- ✅ Ask question → first response chunk in <2 seconds
- ✅ Streaming feels smooth (no lag)
- ✅ Citations accurate (manual spot-check 10 questions)
- ✅ Works on mobile (responsive)

**Portfolio:**
- ✅ Live demo URL (chatpdf.abhishek.oxalate.com)
- ✅ GitHub repo with good README
- ✅ Can explain architecture in interview
- ✅ Can show in Oxalate sales calls

**Monetization (Phase 2, not now):**
- Week 4: Add auth (email/password)
- Week 6: Add Stripe payment
- Week 8: First 10 paying users

---

