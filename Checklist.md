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

## ✅ Phase 2: RAG Pipeline — COMPLETE

### ✅ Already Working (Keep)

- [x] Text chunking with LangChain
- [x] Gemini Embeddings (migrated from local sentence-transformers)
- [x] Streaming chat endpoint (`POST /api/chat` via SSE)
- [x] Citation parsing (regex-based)
- [x] Conversation persistence

### ✅ @backend: Vector Store Migration (Qdrant → ChromaDB) — COMPLETE

**Implemented:** `vector_store.py` uses ChromaDB embedded mode

| Task                                                        | File                           | Status  |
| ----------------------------------------------------------- | ------------------------------ | ------- |
| [x] Replace `qdrant-client` with `chromadb` in requirements | `requirements.txt`             | ✅ Done |
| [x] Rewrite VectorStore class for ChromaDB                  | `app/services/vector_store.py` | ✅ Done |
| [x] Update upload route to use new vector store             | `app/routes/upload.py`         | ✅ Done |
| [x] Test vector operations (add, query, delete)             | Manual                         | ✅ Done |

### ✅ @backend: LLM Migration (Ollama → Gemini Pro) — COMPLETE

**Implemented:** `llm.py` uses `google-genai` SDK

| Task                                              | File                           | Status  |
| ------------------------------------------------- | ------------------------------ | ------- |
| [x] Add `google-genai` to requirements            | `requirements.txt`             | ✅ Done |
| [x] Create GeminiClient class in `llm.py`         | `app/services/llm.py`          | ✅ Done |
| [x] Implement `generate_stream()` with Gemini API | `app/services/llm.py`          | ✅ Done |
| [x] Update `chat_service.py` to use Gemini        | `app/services/chat_service.py` | ✅ Done |
| [x] Add `GEMINI_API_KEY` to `.env`                | `.env`                         | ✅ Done |
| [x] Remove Ollama dependencies                    | `requirements.txt`             | ✅ Done |

---

## 🚀 Phase 4: Deploy & Polish — IN PROGRESS

### 📋 @devops: Backend Deployment (Railway)

| Task                                                                        | Priority | Status  |
| --------------------------------------------------------------------------- | -------- | ------- |
| [x] Create `Dockerfile` optimized for Railway                               | P0       | ✅ Done |
| [x] Configure `railway.json` for deployment                                 | P0       | ✅ Done |
| [x] Fix build size issues (CPU-only torch, remove pysqlite3)                | P0       | ✅ Done |
| [x] Fix startup command (`sh -c` for $PORT expansion)                       | P0       | ✅ Done |
| [ ] Configure persistent storage for `/uploads` and `/data/chroma_db`       | P0       | Pending |
| [ ] Set environment variables in Railway (`GEMINI_API_KEY`, `FRONTEND_URL`) | P0       | Pending |

### 📋 @devops: Frontend Deployment (Vercel)

| Task                                         | Priority | Status  |
| -------------------------------------------- | -------- | ------- |
| [ ] Set `NEXT_PUBLIC_API_URL` to Railway URL | P0       | Pending |
| [ ] Connect GitHub repo                      | P0       | Pending |
| [ ] Test production build                    | P0       | Pending |

### 📋 @qa: End-to-End Testing

| Task                                           | Priority | Status  |
| ---------------------------------------------- | -------- | ------- |
| [x] Upload PDF → verify status becomes "ready" | P0       | ✅ Done |
| [x] Ask question → verify streaming response   | P0       | ✅ Done |
| [x] Verify citations link to correct pages     | P1       | ✅ Done |
| [x] Multi-format document support              | P1       | ✅ Done |
| [x] Document deletion & cleanup                | P1       | ✅ Done |

---

## 🎯 DEPLOYMENT FIXES (Feb 9, 2026)

**1. Docker Optimization**

- Switched to CPU-only PyTorch to reduce image size from >2GB to ~500MB
- Removed `pysqlite3-binary` to avoid build failures

**2. Startup Command**

- Fixed `CMD` to use `sh -c` to correctly expand `$PORT` variable
- Updated `railway.json` to match Dockerfile command

**3. Storage Management**

- Implemented `/api/documents/storage/cleanup` endpoint
- Consolidated file, vector, and DB deletion logic

See [DEPLOY_FIX.md](./DEPLOY_FIX.md) and [STORAGE_MANAGEMENT.md](./STORAGE_MANAGEMENT.md) for details.

### 🧹 Tech Debt Cleanup (Feb 9, 2026) — PENDING

| Task                                                              | File(s)                   | Priority |
| ----------------------------------------------------------------- | ------------------------- | -------- |
| [ ] Migrate from `google.generativeai` to `google.genai` SDK v1.0 | `llm.py`, `embeddings.py` | P1       |
