# ChatPDF Frontend

A modern, responsive Next.js application for chatting with PDF documents using AI.

## 🚀 Features

- **Document Management**: Upload, list, and delete PDF documents.
- **RAG-Powered Chat**: Ask questions across multiple documents with source citations.
- **Real-time Streaming**: AI responses stream in real-time.
- **Responsive UI**: optimized for both desktop and mobile.
- **Persistent History**: Conversations are saved and can be revisited.

## 🛠 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Framer Motion
- **Icons**: Lucide React
- **State Management**: Zustand
- **Components**: Radix UI / Custom Shadcn-like components

## 🏃‍♂️ Getting Started

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Configure Environment**
   Create a `.env.local` file (optional, defaults to localhost:8000):

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

- `/app`: App router pages (`/`, `/chat`, `/upload`)
- `/components`: Reusable UI components (`Sidebar`, `ChatInterface`, etc.)
- `/store`: Zustand state stores (`useChatStore`, `useToastStore`)
- `/lib`: API clients and utilities

## 🧪 Testing

- **Upload Flow**: Drag & drop PDFs in the `/upload` page.
- **Chat Flow**: Navigate to `/chat` and start asking questions.
- **Citations**: Hove over `[Doc, Pg]` citations to see previews.
