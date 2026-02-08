# ChatPDF Project Checklist

## 🛠️ Phase 1: Backend Foundation

- [x] Project setup (FastAPI + Directory Structure)
- [x] Database configuration (PostgreSQL + SQLAlchemy)
- [x] Implement Pydantic Schemas for API validation
- [x] Implement PDF Upload Endpoint (`/api/upload`)
- [x] Implement PDF Text Extraction Service (PyPDF2)
- [x] Implement Document Listing Endpoint (`/api/documents`)
- [x] Basic Error Handling (File size, type validation)
- [x] Integration Testing with `curl`/Postman

## 🧠 Phase 2: RAG Pipeline (AI Logic)

- [x] Implement LangChain Text Splitter (RecursiveCharacterTextSplitter)
- [x] Setup Local Embedding Model (sentence-transformers)
- [x] Setup Qdrant Vector Store integration (Switched from ChromaDB)
- [x] Implement Vector Storage Service (store chunks + metadata)
- [x] Setup Google Gemini Pro API integration (Code ready, needs API Key)
- [x] Implement Streaming Chat Endpoint (`/api/chat` via SSE)
- [x] Implement Citation Parsing Logic (Regex + Metadata matching)
- [x] Add Conversation/Message Persistence in PostgreSQL

## 🎨 Phase 3: Frontend (Next.js 14)

- [x] Project setup (App Router + Tailwind + shadcn/ui)
- [x] Basic App Routing (`/upload`, `/chat`)
- [x] Build Drag-and-Drop Upload Component (react-dropzone)
- [x] Implement Upload Progress UI
- [x] Build Chat Interface Component (Message List + Input)
- [x] Implement SSE Streaming Client for Chat
- [x] Implement Citation Popovers/Tooltips
- [x] Parse `type: citation` in SSE client (`ChatInterface.tsx`)
- [x] Hook up Delete Document functionality (Backend call + UI)
- [x] Populate basic `shadcn/ui` components (Button, Skeleton)
- [x] Setup Zustand Store for global state (messages, docs)

## 🚀 Phase 4: Polish & Deploy

- [x] Security Audit & Hardening:
  - [x] Sanitize CORS (Change `*` to specific origins)
  - [x] Validate `GEMINI_API_KEY` presence on startup
  - [x] File content-type/magic bytes validation
  - [x] Hook VectorStore delete logic to Document route
- [x] UI Polish:
  - [x] Loading skeletons for sidebar and chat
  - [x] Toast notifications for upload success/error
  - [x] Responsive design for mobile (Sidebar toggle implemented)
  - [x] Navigation Sync (Unified /upload and /chat flow)
  - [x] **Premium UI Overhaul**: Glassmorphism, refined typography, and floating interactions.
- [x] Feature Enhancements:
  - [x] Implement Chat Export/Save functionality (Backend implementation complete)
  - [x] Add Conversation Title rename/auto-update (AI auto-gen active)
  - [x] Persistent Chat History (List/Delete conversations in Sidebar)
- [x] Documentation:
  - [x] Create Root `README.md` with setup/env instructions
  - [x] Create Frontend `README.md` with features and usage

## ⚠️ Known Issues / Backlog

- [x] **Rate Limiting**: Switched to `gemini-flash-latest` (stable) to avoid 429 errors.
- [x] **Deprecation**: Migrated to new `google-genai` SDK.
- [x] **Vector Store Locking**: Local Qdrant (file-based) locks if accessed by multiple processes. Added retry mechanism.
- [x] **UI Error Handling**: Ensure 429/500 errors are displayed gracefully to the user.

- [ ] Implement User Auth (Signup/Login/JWT)
- [ ] Deployment: Backend to Railway
- [ ] Deployment: Frontend to Vercel
- [ ] Final End-to-End Testing

---

_Note: Checklist derived from `Plan.md`. Update status as tasks are completed._
