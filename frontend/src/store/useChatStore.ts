import { create } from 'zustand';

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  status: 'processing' | 'ready' | 'failed';
  page_count?: number;
  upload_date: string;
}

export interface Citation {
  document_id: string;
  filename: string;
  page: number;
  chunk_text: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatState {
  documents: Document[];
  conversations: Conversation[];
  messages: Message[];
  currentConversationId: string | null;
  isStreaming: boolean;
  isLoadingDocuments: boolean;
  isLoadingConversations: boolean;
  isLoadingMessages: boolean;
  streamingContent: string;
  streamingCitations: Citation[];
  
  setDocuments: (docs: Document[]) => void;
  setLoadingDocuments: (loading: boolean) => void;
  addDocument: (doc: Document) => void;
  removeDocument: (id: string) => void;
  updateDocumentStatus: (id: string, status: Document['status']) => void;
  
  setConversations: (convs: Conversation[]) => void;
  addConversation: (conv: Conversation) => void;
  removeConversation: (id: string) => void;
  setLoadingConversations: (loading: boolean) => void;
  
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setLoadingMessages: (loading: boolean) => void;
  setStreamingContent: (content: string) => void;
  addStreamingCitation: (citation: Citation) => void;
  setStreamingCitations: (citations: Citation[]) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setCurrentConversationId: (id: string | null) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  documents: [],
  conversations: [],
  messages: [],
  currentConversationId: null,
  isStreaming: false,
  isLoadingDocuments: false,
  isLoadingConversations: false,
  isLoadingMessages: false,
  streamingContent: '',
  streamingCitations: [],

  setDocuments: (documents) => set({ documents }),
  setLoadingDocuments: (isLoadingDocuments) => set({ isLoadingDocuments }),
  addDocument: (doc) => set((state) => ({ documents: [doc, ...state.documents] })),
  removeDocument: (id) => set((state) => ({
    documents: state.documents.filter((doc) => doc.id !== id)
  })),
  updateDocumentStatus: (id, status) => set((state) => ({
    documents: state.documents.map((doc) => doc.id === id ? { ...doc, status } : doc)
  })),

  setConversations: (conversations) => set({ conversations }),
  addConversation: (conv) => set((state) => ({ 
    conversations: [conv, ...state.conversations.filter(c => c.id !== conv.id)] 
  })),
  removeConversation: (id) => set((state) => ({
    conversations: state.conversations.filter(c => c.id !== id),
    currentConversationId: state.currentConversationId === id ? null : state.currentConversationId,
    messages: state.currentConversationId === id ? [] : state.messages
  })),
  setLoadingConversations: (isLoadingConversations) => set({ isLoadingConversations }),

  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setLoadingMessages: (isLoadingMessages) => set({ isLoadingMessages }),
  setStreamingContent: (content) => set({ streamingContent: content }),
  addStreamingCitation: (citation) => set((state) => ({ 
    streamingCitations: [...state.streamingCitations, citation] 
  })),
  setStreamingCitations: (citations) => set({ streamingCitations: citations }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setCurrentConversationId: (id) => set({ currentConversationId: id }),
}));
