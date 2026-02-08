# ChatDoc: AI-Powered Multi-Document Chat

ChatDoc is a full-stack application that allows you to upload multiple documents (PDF, DOCX, TXT, MD, HTML) and interact with them using a conversational AI. Built with **Next.js 14**, **FastAPI**, **ChromaDB**, and **Google Gemini Pro**.

## 🚀 Features

- **Multi-Format Support**: Upload PDF, DOCX, DOC, TXT, MD, and HTML files.
- **Multi-Document RAG**: Chat across multiple uploaded documents simultaneously.
- **Streaming Responses**: Real-time AI response streaming with citation support.
- **Context-Aware Citations**: Clickable source citations with text snippets and page numbers.
- **Premium UI**: Modern, dark-mode first design with glassmorphism and animations.
- **Responsive Design**: Fully functional on desktop and mobile devices.
- **Embedded Vector Store**: ChromaDB runs locally, no external services needed.

## 🛠️ Tech Stack

### Frontend

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Custom Design System
- **State Management**: Zustand
- **Components**: shadcn/ui (Icons by Lucide)
- **Animations**: Framer Motion

### Backend

- **Framework**: FastAPI (Python 3.12+)
- **Database**: SQLite with SQLAlchemy ORM
- **Vector Store**: ChromaDB (Embedded Mode)
- **AI/LLM**: Google Gemini 2.0 Flash API
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Document Processing**: PyPDF2, python-docx, BeautifulSoup4, LangChain

## 📦 Installation & Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google Gemini API Key (Free tier available)

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
   DATABASE_URL=sqlite:///./chatpdf.db
   GEMINI_API_KEY=your_gemini_api_key
   CHROMA_PERSIST_DIR=/data/chroma_db
   UPLOAD_DIRECTORY=./uploads
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
│   │   ├── services/       # RAG, Document Processing & LLM Logic
│   │   └── models.py       # Database Schemas
│   ├── uploads/            # Document Storage
│   └── chroma_db/          # ChromaDB Vector Storage
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
