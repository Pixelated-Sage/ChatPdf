'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  Plus, 
  MessageSquare, 
  Files, 
  Trash2, 
  FileText, 
  Settings,
  HelpCircle,
  Menu,
  X,
  History,
  MessageCircle,
  Sparkles,
  Upload,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { deleteDocument as deleteDocumentApi, deleteConversation as deleteConversationApi } from '@/lib/api';
import { useToastStore } from '@/store/useToastStore';
import { Skeleton } from '@/components/ui/skeleton';

export const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [isOpen, setIsOpen] = React.useState(false);
  
  const { 
    documents, 
    conversations,
    isLoadingDocuments, 
    isLoadingConversations,
    removeDocument, 
    removeConversation,
    currentConversationId,
    setCurrentConversationId,
    setMessages
  } = useChatStore();
  
  const addToast = useToastStore((state) => state.addToast);

  const isChat = pathname === '/chat';

  const handleDeleteDocument = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this document?')) return;
    try {
      await deleteDocumentApi(id);
      removeDocument(id);
      addToast('Document deleted', 'success');
    } catch (err) {
      addToast('Failed to delete document', 'error');
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this chat?')) return;
    try {
      await deleteConversationApi(id);
      removeConversation(id);
      addToast('Chat deleted', 'success');
    } catch (err) {
      addToast('Failed to delete chat', 'error');
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    router.push('/chat');
    setIsOpen(false);
  };

  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
    router.push('/chat');
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile Toggle */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-xl bg-background border border-border/50 shadow-lg sm:hidden text-foreground"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm sm:hidden"
          />
        )}
      </AnimatePresence>

      <aside className={cn(
        "fixed left-0 top-0 z-40 h-screen w-72 border-r border-border bg-sidebar transition-transform sm:translate-x-0 shadow-2xl sm:shadow-none",
        !isOpen && "-translate-x-full"
      )}>
        <div className="flex h-full flex-col p-4">
          {/* Brand */}
          <Link href="/" className="mb-8 flex items-center gap-3 px-2 hover:opacity-80 transition-opacity cursor-pointer">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
              <Sparkles size={18} />
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight text-foreground">ChatPDF</span>
              <span className="text-[10px] text-muted-foreground font-medium tracking-wider uppercase">Pro Workspace</span>
            </div>
          </Link>

          {/* Primary Actions */}
          <div className="space-y-2 mb-8">
            <button 
              onClick={handleNewChat}
              className={cn(
                "group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 border",
                isChat && !currentConversationId 
                  ? "bg-primary/10 text-primary border-primary/20 shadow-sm" 
                  : "bg-background text-foreground hover:bg-accent border-border/50 shadow-sm"
              )}
            >
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-background group-hover:bg-primary/10 transition-colors">
                <Plus size={14} className="text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              New Chat
            </button>
            <Link 
              href="/upload"
              onClick={() => setIsOpen(false)}
              className={cn(
                "group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 border border-transparent",
                pathname === '/upload'
                  ? "bg-accent/80 text-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <Files size={18} />
              Document Library
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto overflow-x-hidden space-y-8 pr-2 custom-scrollbar">
            {/* Recent Conversations */}
            <div>
              <div className="mb-3 px-2 flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-muted-foreground/60">
                <span>Recent History</span>
              </div>
              <div className="space-y-0.5">
                {isLoadingConversations ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-9 w-full rounded-md bg-secondary/50 mb-1" />
                  ))
                ) : conversations.length === 0 ? (
                  <p className="px-2 py-4 text-xs text-muted-foreground/50 text-center border border-dashed border-border/50 rounded-lg">
                    No active chats
                  </p>
                ) : (
                  conversations.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv.id)}
                      className={cn(
                        "group relative flex cursor-pointer items-center gap-3 rounded-md px-2.5 py-2 text-sm transition-all duration-200",
                        currentConversationId === conv.id 
                          ? "bg-accent text-foreground font-medium" 
                          : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                      )}
                    >
                      <MessageCircle size={14} className={cn(
                        "shrink-0 transition-colors",
                         currentConversationId === conv.id ? "text-primary" : "text-muted-foreground/50 group-hover:text-muted-foreground"
                      )} />
                      <span className="truncate flex-1">{conv.title || 'Untitled Conversation'}</span>
                      <button 
                        onClick={(e) => handleDeleteConversation(conv.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 hover:text-destructive rounded transition-all"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Quick Access Documents */}
            <div>
              <div className="mb-3 px-2 flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-muted-foreground/60">
                <span>Documents</span>
                <Link href="/upload" className="text-[10px] hover:text-primary transition-colors cursor-pointer">+ Add</Link>
              </div>
              <div className="space-y-1.5">
                {isLoadingDocuments ? (
                  // Enhanced Loading Skeletons
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-2.5 px-2 py-2 rounded-md">
                      <Skeleton className="h-7 w-7 rounded-md" />
                      <div className="flex-1 space-y-1.5">
                        <Skeleton className="h-3 w-3/4 rounded" />
                        <Skeleton className="h-2 w-1/3 rounded" />
                      </div>
                    </div>
                  ))
                ) : documents.length === 0 ? (
                  // Enhanced Empty State
                  <Link 
                    href="/upload"
                    className="flex flex-col items-center gap-3 py-6 px-4 border border-dashed border-border/60 rounded-xl hover:border-primary/40 hover:bg-primary/5 transition-all cursor-pointer group"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
                      <Upload size={18} />
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-semibold text-foreground/80">No documents yet</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">Click to upload your first PDF</p>
                    </div>
                  </Link>
                ) : (
                  documents.slice(0, 5).map((doc) => (
                    <div
                      key={doc.id}
                      className="group flex items-center gap-2.5 rounded-lg px-2 py-2 text-xs text-muted-foreground hover:bg-accent/40 transition-all cursor-default"
                    >
                      {/* Status-aware Icon */}
                      <div className={cn(
                        "relative flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border transition-colors",
                        doc.status === 'ready' && "border-emerald-500/30 bg-emerald-500/10 text-emerald-500",
                        doc.status === 'processing' && "border-amber-500/30 bg-amber-500/10 text-amber-500",
                        doc.status === 'failed' && "border-rose-500/30 bg-rose-500/10 text-rose-500"
                      )}>
                        {doc.status === 'processing' ? (
                          <Loader2 size={13} className="animate-spin" />
                        ) : doc.status === 'failed' ? (
                          <AlertCircle size={13} />
                        ) : (
                          <FileText size={13} />
                        )}
                      </div>
                      
                      {/* Document Info */}
                      <div className="flex-1 min-w-0">
                        <p className="truncate text-[11px] font-medium text-foreground/80 group-hover:text-foreground">
                          {doc.original_filename}
                        </p>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          {/* Status Badge */}
                          <span className={cn(
                            "inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider",
                            doc.status === 'ready' && "text-emerald-500",
                            doc.status === 'processing' && "text-amber-500",
                            doc.status === 'failed' && "text-rose-500"
                          )}>
                            {doc.status === 'ready' && <CheckCircle2 size={8} />}
                            {doc.status === 'processing' && <Loader2 size={8} className="animate-spin" />}
                            {doc.status === 'failed' && <AlertCircle size={8} />}
                            {doc.status}
                          </span>
                          {doc.page_count && (
                            <span className="text-[9px] text-muted-foreground/60">• {doc.page_count} pages</span>
                          )}
                        </div>
                      </div>

                      {/* Delete Button */}
                      <button 
                        onClick={(e) => handleDeleteDocument(doc.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-destructive/10 hover:text-destructive rounded-md transition-all"
                        title="Delete document"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* User / Settings Footer */}
          <div className="mt-4 border-t border-border pt-4">
            <div className="flex items-center gap-3 rounded-xl bg-accent/50 p-3 border border-border/50">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-violet-700 flex items-center justify-center text-white text-xs font-bold shadow-inner">
                AB
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-sm font-medium text-foreground">Abhishek</p>
                <p className="truncate text-[10px] text-muted-foreground">Pro Plan</p>
              </div>
              <button className="text-muted-foreground hover:text-foreground transition-colors">
                <Settings size={16} />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
