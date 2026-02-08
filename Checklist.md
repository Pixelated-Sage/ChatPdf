# ChatPDF v2 - Project Checklist

> **Stack:** FastAPI + Next.js 14 + ChromaDB + Gemini Pro API  
> **Updated:** 2026-02-08  
> **Reference:** [Plan.md](./Plan.md)

---

## 📊 STATUS OVERVIEW

| Phase   | Description        | Status             |
| ------- | ------------------ | ------------------ |
| Phase 1 | Backend Foundation | ✅ Complete        |
| Phase 2 | RAG Pipeline       | ⚠️ Needs Migration |
| Phase 3 | Frontend           | ✅ Complete        |
| Phase 4 | Deploy & Polish    | ❌ Not Started     |

---

## ✅ Phase 1: Backend Foundation — COMPLETE

All items already implemented:

- [x] FastAPI project structure (`app/main.py`)
- [x] SQLite database with SQLAlchemy ORM (`database.py`)
- [x] Pydantic schemas (`schemas.py`)
- [x] Config with BaseSettings (`config.py`)
- [x] PDF upload endpoint (`POST /api/upload`)
- [x] PDF text extraction (`pdf_processor.py`)
- [x] Document list endpoint (`GET /api/documents`)
- [x] Document delete endpoint (`DELETE /api/documents/{id}`)
- [x] CORS configuration
- [x] Error handling (file size, type validation)

---

## ⚠️ Phase 2: RAG Pipeline — MIGRATION REQUIRED

### ✅ Already Working (Keep)

- [x] Text chunking with LangChain
- [x] Local embeddings (sentence-transformers/all-MiniLM-L6-v2)
- [x] Streaming chat endpoint (`POST /api/chat` via SSE)
- [x] Citation parsing (regex-based)
- [x] Conversation persistence

### 🔄 @backend: Vector Store Migration (Qdrant → ChromaDB)

**Current:** `vector_store.py` uses Qdrant  
**Target:** ChromaDB (per Plan.md - no separate server needed)

| Task                                                        | File                           | Priority |
| ----------------------------------------------------------- | ------------------------------ | -------- |
| [ ] Replace `qdrant-client` with `chromadb` in requirements | `requirements.txt`             | P0       |
| [ ] Rewrite VectorStore class for ChromaDB                  | `app/services/vector_store.py` | P0       |
| [ ] Update upload route to use new vector store             | `app/routes/upload.py`         | P0       |
| [ ] Test vector operations (add, query, delete)             | Manual                         | P0       |

**ChromaDB API (from Plan.md):**

```python
# Persist to ./chroma_db directory
client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = client.get_or_create_collection("pdf_chunks")

# Add documents
collection.add(ids=[...], embeddings=[...], metadatas=[...], documents=[...])

# Query
results = collection.query(query_embeddings=[...], n_results=5)

# Delete
collection.delete(where={"document_id": doc_id})
```

---

### 🔄 @backend: LLM Migration (Ollama → Gemini Pro)

**Current:** `llm.py` has `OllamaClient`  
**Target:** Gemini Pro API (free till April 2026, works on Railway)

| Task                                              | File                           | Priority |
| ------------------------------------------------- | ------------------------------ | -------- |
| [ ] Add `google-generativeai` to requirements     | `requirements.txt`             | P0       |
| [ ] Create GeminiClient class in `llm.py`         | `app/services/llm.py`          | P0       |
| [ ] Implement `generate_stream()` with Gemini API | `app/services/llm.py`          | P0       |
| [ ] Update `chat_service.py` to use Gemini        | `app/services/chat_service.py` | P0       |
| [ ] Add `GEMINI_API_KEY` to `.env.example`        | `.env.example`                 | P0       |
| [ ] Remove Ollama dependencies                    | `requirements.txt`             | P1       |

**Gemini Streaming (from Plan.md):**

```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Streaming
for chunk in model.generate_content(prompt, stream=True):
    yield chunk.text
```

---

## ✅ Phase 3: Frontend — COMPLETE

All items already implemented:

- [x] Next.js 14 (App Router + TypeScript)
- [x] Tailwind CSS + shadcn/ui
- [x] Zustand state management
- [x] Drag-drop upload (`DocumentUploader.tsx`)
- [x] Upload progress indicator
- [x] Chat interface (`ChatInterface.tsx`)
- [x] SSE streaming client
- [x] Citation display
- [x] Document sidebar (`Sidebar.tsx`)
- [x] Conversation history
- [x] Responsive design
- [x] Dark mode support

### ✅ @frontend: Polish Tasks — COMPLETE

| Task                                                 | File                | Status  |
| ---------------------------------------------------- | ------------------- | ------- |
| [x] Enhanced loading skeletons for document list     | `Sidebar.tsx`       | ✅ Done |
| [x] Empty state when no documents (with upload CTA)  | `Sidebar.tsx`       | ✅ Done |
| [x] Document status badges (processing/ready/failed) | `Sidebar.tsx`       | ✅ Done |
| [x] Empty state when no documents in chat            | `ChatInterface.tsx` | ✅ Done |

---

## ❌ Phase 4: Deploy & Polish — NOT STARTED

### 📋 @devops: Backend Deployment (Railway)

| Task                                                                            | Priority |
| ------------------------------------------------------------------------------- | -------- |
| [ ] Create `Procfile` (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`) | P0       |
| [ ] Configure persistent storage for `/uploads` and `/chroma_db`                | P0       |
| [ ] Set environment variables (`GEMINI_API_KEY`, `DATABASE_URL`)                | P0       |
| [ ] Test API endpoints via curl                                                 | P0       |

### 📋 @devops: Frontend Deployment (Vercel)

| Task                                         | Priority |
| -------------------------------------------- | -------- |
| [ ] Set `NEXT_PUBLIC_API_URL` to Railway URL | P0       |
| [ ] Connect GitHub repo                      | P0       |
| [ ] Test production build                    | P0       |

### 📋 @qa: End-to-End Testing

| Task                                           | Priority |
| ---------------------------------------------- | -------- |
| [ ] Upload PDF → verify status becomes "ready" | P0       |
| [ ] Ask question → verify streaming response   | P0       |
| [ ] Verify citations link to correct pages     | P1       |
| [ ] Test mobile responsiveness                 | P1       |

---

## 🎯 PRIORITY ORDER (To Get Working)

```
1. [P0] @backend: Replace Qdrant → ChromaDB in vector_store.py
2. [P0] @backend: Replace Ollama → Gemini Pro in llm.py
3. [P0] @backend: Update requirements.txt
4. [P0] @backend: Test end-to-end locally
5. [P0] @devops: Deploy backend to Railway
6. [P0] @devops: Deploy frontend to Vercel
7. [P1] @qa: Full testing
```

---

## 📁 Files to Modify

| File                           | Action                                                        | Owner    |
| ------------------------------ | ------------------------------------------------------------- | -------- |
| `requirements.txt`             | Remove `qdrant-client`, add `chromadb`, `google-generativeai` | @backend |
| `app/services/vector_store.py` | Rewrite for ChromaDB                                          | @backend |
| `app/services/llm.py`          | Replace OllamaClient with GeminiClient                        | @backend |
| `app/services/chat_service.py` | Update LLM import                                             | @backend |
| `.env.example`                 | Add `GEMINI_API_KEY`, remove Ollama vars                      | @backend |

---

## 🔧 Environment Variables (Updated)

### Backend `.env`

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults work)
DATABASE_URL=sqlite:///./app.db
UPLOAD_DIR=./uploads
CHROMA_DIR=./chroma_db
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=http://localhost:3000,https://chatpdf.vercel.app
```

### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

_Last updated: 2026-02-08 | Aligned with Plan.md v2_

### ✅ Navigation & UX Fixes (Feb 8, 2026) — COMPLETE

| Task                                              | File(s)                                    | Status  |
| ------------------------------------------------- | ------------------------------------------ | ------- |
| [x] Make ChatPDF logo clickable (links to home)   | `Sidebar.tsx`, `page.tsx`                  | ✅ Done |
| [x] Fix misleading "Log in" label to "Upload"     | `page.tsx`                                 | ✅ Done |
| [x] Multi-format document support (DOCX, TXT, MD) | `api.ts`, `DocumentUploader.tsx`, Backend  | ✅ Done |
| [x] Document format validation on upload          | `api.ts`, `DocumentUploader.tsx`           | ✅ Done |

**See:** `NAVIGATION_FIXES.md` for detailed documentation.

