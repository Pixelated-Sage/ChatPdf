# ChatPDF — Project Documentation

This document describes the backend and frontend structure, how each key file works, the runtime flow, and the HTTP APIs used by the frontend.

---

## Project Overview
- Backend: FastAPI application that handles uploads, document processing, vector storage (ChromaDB), embeddings (Gemini/Google GenAI), and a RAG-based chat endpoint.
- Frontend: Next.js (App Router) UI for uploading documents, viewing conversations, and chatting. Uses client-side streaming to render LLM responses.

---

## How data flows (high level)
1. User uploads a document from the frontend.
2. Frontend calls `POST /api/upload` → backend saves file, creates a DB record, and enqueues background processing.
3. Background processor extracts text/pages, chunks text, computes embeddings (Gemini), and stores chunks+embeddings in ChromaDB persistent collection.
4. User asks a question from the frontend; frontend calls `POST /api/chat`.
5. Backend embeds the query, queries the vector store for top chunks, builds a RAG prompt, streams token output from Gemini back to the client using Server-Sent Events (SSE).
6. Backend persists the assistant message and citations to the DB when streaming completes.

---

## Backend — important files and their responsibilities

- `backend/app/main.py` — Application startup, CORS, route registration, health checks, and debug endpoints. (Entry point for FastAPI app.)
  - See [backend/app/main.py](backend/app/main.py#L1-L120) for startup lifecycle and health endpoints.

- `backend/app/config.py` — Centralized configuration using `pydantic-settings` (`Settings`). Environment variables: `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `CHROMA_PERSIST_DIR`, `UPLOAD_DIRECTORY`, etc.
  - See [backend/app/config.py](backend/app/config.py#L1-L80).

- `backend/app/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, and `get_db()` dependency used by route handlers.
  - See [backend/app/database.py](backend/app/database.py#L1-L60).

- `backend/app/models.py` — SQLAlchemy models: `Document`, `Conversation`, `Message`, and association table `conversation_documents`.
  - See [backend/app/models.py](backend/app/models.py#L1-L200).

- `backend/app/schemas.py` — Pydantic schemas used for request/response validation and serialization.
  - See [backend/app/schemas.py](backend/app/schemas.py#L1-L200).

### Routers (HTTP endpoints)
- `backend/app/routes/upload.py` — `POST /api/upload`
  - Validates uploads, saves file on disk, creates a DB `Document` row, and enqueues background processing via FastAPI `BackgroundTasks`.
  - Background processing steps: extract pages, chunk pages, embed chunks via `embedding_service`, store chunks & metadatas in `vector_store`.
  - See [backend/app/routes/upload.py](backend/app/routes/upload.py#L1-L220).

- `backend/app/routes/documents.py` — Document management
  - `GET /api/documents` — list documents
  - `GET /api/documents/{document_id}` — get document metadata
  - `DELETE /api/documents/{document_id}` — deletes physical file, vectors from Chroma, and DB record
  - `GET /api/documents/storage/stats` and `POST /api/documents/storage/cleanup` — storage diagnostics and orphan cleanup
  - See [backend/app/routes/documents.py](backend/app/routes/documents.py#L1-L300).

- `backend/app/routes/conversations.py` — Conversations and messages
  - `GET /api/conversations` — list conversations
  - `GET /api/conversations/{id}` — get conversation
  - `GET /api/conversations/{id}/messages` — list messages for conversation
  - `DELETE /api/conversations/{id}` — delete conversation
  - `GET /api/conversations/{id}/export` — export conversation as markdown payload
  - `PATCH /api/conversations/{id}/rename` — rename conversation
  - See [backend/app/routes/conversations.py](backend/app/routes/conversations.py#L1-L220).

- `backend/app/routes/chat.py` — Core chat endpoint
  - `POST /api/chat` accepts `ChatRequest` (question, optional conversation_id, optional document_ids)
  - Creates conversation if needed, saves user message, runs RAG pipeline via `chat_service.generate_answer` which streams events (chunk/citation/done) back to client as SSE.
  - On `done` event, persists assistant message (with citations) to DB.
  - See [backend/app/routes/chat.py](backend/app/routes/chat.py#L1-L240).

### Services (business logic)
- `backend/app/services/document_processor.py` — generic document extraction and chunking. Supports PDF, DOCX, TXT, MD, HTML. Uses `PyPDF2`, `python-docx`, `BeautifulSoup` and `langchain_text_splitters`.
  - Provides `extract_pages`, `get_metadata`, `chunk_text`, and `is_supported`.
  - See [backend/app/services/document_processor.py](backend/app/services/document_processor.py#L1-L220).

- `backend/app/services/embeddings.py` — wraps Google GenAI (Gemini) embeddings via `google.genai` client. Exposes `embedding_service.embed_text` and `embed_chunks`.
  - See [backend/app/services/embeddings.py](backend/app/services/embeddings.py#L1-L240).

- `backend/app/services/vector_store.py` — ChromaDB persistent collection wrapper. Stores chunk texts, embeddings, metadatas and exposes `add_chunks`, `query`, `delete_document`, and `get_collection_stats`.
  - Uses a custom `GeminiEmbeddingFunction` so Chroma calls your embedding pipeline.
  - See [backend/app/services/vector_store.py](backend/app/services/vector_store.py#L1-L280).

- `backend/app/services/llm.py` — low-level Gemini client wrapper. Provides `generate_stream`, `generate`, and `build_rag_prompt` helpers.
  - See [backend/app/services/llm.py](backend/app/services/llm.py#L1-L220).

- `backend/app/services/chat_service.py` — orchestrates RAG: embed query → query vector store → build prompt → stream LLM output → parse citations → yield SSE events.
  - Public API used by router: `chat_service.generate_answer(question, doc_ids)` and `chat_service.generate_title(first_message)`.
  - See [backend/app/services/chat_service.py](backend/app/services/chat_service.py#L1-L320).

---

## Frontend — important files and responsibilities

- `frontend/src/lib/api.ts` — client-side HTTP wrapper. Knows the backend base URL (`NEXT_PUBLIC_API_URL` or default) and provides functions: `uploadDocument`, `getDocumentStatus`, `listDocuments`, `deleteDocument`, `listConversations`, `getConversationMessages`, `chat`, `exportConversation`, `renameConversation`.
  - See [frontend/src/lib/api.ts](frontend/src/lib/api.ts#L1-L220).

- `frontend/src/components/DocumentUploader.tsx` — Dropzone UI, file validation, calls `uploadDocument`, adds document stub to the app store, and triggers background indexing message UI.
  - See [frontend/src/components/DocumentUploader.tsx](frontend/src/components/DocumentUploader.tsx#L1-L260).

- `frontend/src/components/ChatInterface.tsx` — Chat UI, SSE handling and streaming response parsing, shows citations and messages, manages input and submission.
  - Key behaviour: reads `response.body` from `chat()` call, decodes SSE `data: ...` lines, updates store with streaming chunks, stores final assistant message on `done`.
  - See [frontend/src/components/ChatInterface.tsx](frontend/src/components/ChatInterface.tsx#L1-L420).

- `frontend/src/store/useChatStore.ts` — Zustand store for documents, conversations, messages, streaming state and helper actions used across components.
  - See [frontend/src/store/useChatStore.ts](frontend/src/store/useChatStore.ts#L1-L200).

- Pages (App Router):
  - `frontend/src/app/upload/page.tsx` — Upload page that renders `DocumentUploader` and `Sidebar`.
  - `frontend/src/app/chat/page.tsx` — Chat page (not explicitly printed here) renders `ChatInterface`.

---

## HTTP API Summary (endpoints used by frontend)

- POST /api/upload
  - Request: multipart/form-data with `file`
  - Response: 202 queued response with `document_id`, `filename`, `status`, `message`.

- GET /api/documents
  - List documents (metadata)

- GET /api/documents/{document_id}
  - Document metadata and processing status

- DELETE /api/documents/{document_id}
  - Deletes file, vectors, DB record

- POST /api/chat
  - Request JSON: { question, document_ids?: string[], conversation_id?: string }
  - Response: SSE stream with `data: {...}` events. Event types: `start`, `chunk`, `citation`, `done`, `error`.

- GET /api/conversations
- GET /api/conversations/{id}/messages
- DELETE /api/conversations/{id}
- PATCH /api/conversations/{id}/rename
- GET /api/conversations/{id}/export

---

## Environment & configuration

- Backend env variables (via `.env` or environment):
  - `DATABASE_URL` — SQLAlchemy database URL (default sqlite local)
  - `GEMINI_API_KEY` — Gemini / Google GenAI API key (required for embeddings & LLM)
  - `GEMINI_MODEL` — model identifier (default in `config.py`)
  - `CHROMA_PERSIST_DIR` — persistence directory for ChromaDB
  - `UPLOAD_DIRECTORY` — uploads directory
  - `NEXT_PUBLIC_API_URL` — frontend can override API base

---

## How to run locally

- Backend (from `backend/`):
  1. Create a virtualenv and install deps: `pip install -r requirements.txt`.
  2. Add `.env` with `GEMINI_API_KEY` (and other overrides as needed).
  3. Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

- Frontend (from `frontend/`):
  1. Install: `npm install` or `pnpm install`.
  2. Run dev server: `npm run dev`.
  3. Ensure `NEXT_PUBLIC_API_URL` points to backend (default `http://localhost:8000`).

---

## Notes, caveats, and suggestions

- Streaming: The chat endpoint uses native SSE streaming of JSON events; the frontend parses `data: ...` lines from the response body and updates the UI incrementally.
- Long-running processing: Document processing is done in FastAPI `BackgroundTasks` (sufficient for small scale). For more scale, consider using a job queue (Redis + RQ/Celery) to avoid blocking in-process resources.
- Chroma persistence: the vector store uses local disk persistence. For production, choose durable storage or hosted vector DB.
- Error handling: many operations swallow exceptions and return messages — add more structured logging and alerting for production.

---

If you'd like, I can:
- Generate a condensed OpenAPI-style list of endpoints (with request/response examples), or
- Create a developer `README.md` with quick start scripts and docker instructions.

End of documentation.
