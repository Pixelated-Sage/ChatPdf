# ChatPDF: AI-Powered Multi-Document Chat

ChatPDF is a full-stack application that allows you to upload multiple PDF documents and interact with them using a conversational AI. Built with **Next.js 14**, **FastAPI**, **PostgreSQL**, **Qdrant**, and **Google Gemini Pro**.

## 🚀 Features

- **Multi-Document RAG**: Chat across multiple uploaded PDFs simultaneously.
- **Streaming Responses**: Real-time AI response streaming via SSE.
- **Context-Aware Citations**: Clickable source citations with text snippets and page numbers.
- **Premium UI**: Modern, dark-mode first design with glassmorphism and animations.
- **Responsive Design**: Fully functional on desktop and mobile devices.
- **Vector Search**: High-performance semantic search powered by Qdrant and Sentence Transformers.

## 🛠️ Tech Stack

### Frontend

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Custom Design System
- **State Management**: Zustand
- **Components**: shadcn/ui (Icons by Lucide)
- **Animations**: Framer Motion

### Backend

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Store**: Qdrant (Local)
- **AI/LLM**: Google Gemini Pro API
- **Embeddings**: Sentence-Transformers (Local)
- **PDF Processing**: PyPDF2 + LangChain

## 📦 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Google Gemini API Key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (Create `.env`):
   ```env
   DATABASE_URL=postgresql://user:password@localhost/chatpdf
   GEMINI_API_KEY=your_gemini_api_key
   ```
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables (Create `.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

## 📁 Project Structure

```
.
├── backend/                # FastAPI Application
│   ├── app/                # Application Logic
│   │   ├── routes/         # API Endpoints
│   │   ├── services/       # RAG, PDF & LLM Logic
│   │   └── models.py       # Database Schemas
│   ├── uploads/            # Temporary PDF Storage
│   └── qdrant_data/        # Local Vector Storage
├── frontend/               # Next.js Application
│   ├── src/
│   │   ├── app/            # App Router Pages
│   │   ├── components/     # UI Components
│   │   ├── lib/            # API Clients & Utils
│   │   └── store/          # Zustand Global State
└── Checklist.md            # Project Roadmap
```

## ⚖️ License

MIT
