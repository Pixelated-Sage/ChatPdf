'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Send, User, Bot, Quote, Copy, Download, Loader2, Info, MessageCircle, Sparkles, RefreshCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore, Message } from '@/store/useChatStore';
import { cn } from '@/lib/utils';
import { chat as chatApi, getConversationMessages, listConversations } from '@/lib/api';
import { useToastStore } from '@/store/useToastStore';

export const ChatInterface = () => {
  const { 
    messages, 
    setMessages, 
    addMessage, 
    isStreaming, 
    setIsStreaming, 
    streamingContent, 
    setStreamingContent, 
    streamingCitations,
    setStreamingCitations,
    addStreamingCitation,
    currentConversationId,
    setCurrentConversationId,
    setConversations,
    documents
  } = useChatStore();
  
  const [input, setInput] = useState('');
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const addToast = useToastStore(state => state.addToast);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      const loadMessages = async () => {
        setIsLoadingMessages(true);
        try {
          const fetchedMessages = await getConversationMessages(currentConversationId);
          setMessages(fetchedMessages);
        } catch (err) {
          console.error('Failed to load messages', err);
          addToast('Failed to load chat history', 'error');
        } finally {
          setIsLoadingMessages(false);
        }
      };
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [currentConversationId, setMessages, addToast]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      created_at: new Date().toISOString()
    };

    addMessage(userMessage);
    const question = input;
    setInput('');
    setIsStreaming(true);
    setStreamingContent('');
    setStreamingCitations([]);

    try {
      const activeDocs = documents.filter(d => d.status === 'ready');
      if (activeDocs.length === 0) {
        addToast('No ready documents found. Upload some PDFs first!', 'info');
      }

      const selectedDocIds = activeDocs.map(d => d.id);
      const response = await chatApi(question, selectedDocIds, currentConversationId || undefined);
      
      if (!response.ok) {
        let errorMessage = 'Network response was not ok';
        try {
          const errData = await response.json();
          errorMessage = errData.detail || errData.error || errorMessage;
        } catch (e) {
             // ignore json parse error
        }

        if (response.status === 429) {
          errorMessage = 'Too many requests. Please wait a moment before trying again.';
        }
        throw new Error(errorMessage);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      let fullContent = '';
      
      while (true) {
        const { done, value } = await reader?.read() || { done: true, value: undefined };
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'start') {
                if (data.conversation_id && !currentConversationId) {
                  setCurrentConversationId(data.conversation_id);
                  // Refresh conversation list to get the new title
                  const convs = await listConversations();
                  setConversations(convs);
                }
              } else if (data.type === 'chunk') {
                fullContent += data.content;
                setStreamingContent(fullContent);
              } else if (data.type === 'citation') {
                addStreamingCitation(data.data);
              } else if (data.type === 'done') {
                const assistantMessage: Message = {
                  id: Date.now().toString(),
                  role: 'assistant',
                  content: data.full_content || fullContent,
                  citations: data.citations || useChatStore.getState().streamingCitations,
                  created_at: new Date().toISOString(),
                };
                addMessage(assistantMessage);
                setStreamingContent('');
                setStreamingCitations([]);
              } else if (data.type === 'error') {
                addToast(data.content, 'error');
              }
            } catch (e) {
              console.error('Error parsing SSE chunk', e);
            }
          }
        }
      }

    } catch (err: any) {
      console.error('Chat error', err);
      addToast(err.message || 'Connection failed', 'error');
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-background relative isolate">
      {/* Header Info */}
      <div className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 py-4 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <MessageCircle size={18} />
          </div>
          <div>
            <h1 className="text-sm font-semibold truncate max-w-[200px] text-foreground">
              {currentConversationId 
                ? useChatStore.getState().conversations.find(c => c.id === currentConversationId)?.title || 'Discussion'
                : 'New Conversation'}
            </h1>
            <p className="text-[10px] text-muted-foreground font-medium">
              {documents.filter(d => d.status === 'ready').length} source(s) active
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
           {/* Actions - Future Impl */}
        </div>
      </div>

      {/* Message List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-8 pt-24 space-y-8 scroll-smooth custom-scrollbar"
      >
        {isLoadingMessages ? (
          <div className="flex flex-col gap-8 max-w-4xl mx-auto w-full">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className={cn("flex gap-4 w-full", i % 2 === 0 ? "justify-end" : "justify-start")}>
                 <div className={cn("h-24 w-2/3 rounded-2xl animate-pulse", i % 2 === 0 ? "bg-secondary/50" : "bg-card border border-border/50")} />
              </div>
            ))}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto w-full space-y-8 pb-32">
            <AnimatePresence initial={false} mode="popLayout">
              {messages.length === 0 && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center justify-center space-y-6 pt-12"
                >
                  <div className="relative group">
                    <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full group-hover:bg-primary/30 transition-all duration-500" />
                    <div className="relative flex h-20 w-20 items-center justify-center rounded-3xl bg-secondary border border-border shadow-xl">
                      <Sparkles size={32} className="text-primary" />
                    </div>
                  </div>
                  
                  <div className="text-center max-w-md space-y-2">
                    <h2 className="text-2xl font-bold tracking-tight text-foreground">Knowledge Assistant</h2>
                    <p className="text-sm text-muted-foreground">
                      Ask questions about your uploaded PDFs. I can summarize, compare, and cite specific pages.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 w-full max-w-lg mt-8">
                    {[
                      { l: 'Summarize key insights', i: <Info size={14} /> },
                      { l: 'Identify risks & terms', i: <Info size={14} /> },
                      { l: 'Compare documents', i: <RefreshCcw size={14} /> },
                      { l: 'Find specific data', i: <Sparkles size={14} /> }
                    ].map((hint) => (
                      <button 
                        key={hint.l}
                        onClick={() => setInput(hint.l)}
                        className="flex items-center gap-2 px-4 py-3 text-xs font-medium rounded-xl border border-border bg-card/50 hover:bg-accent hover:border-primary/30 transition-all text-left group"
                      >
                       <span className="text-muted-foreground group-hover:text-primary transition-colors">{hint.i}</span> 
                       {hint.l}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {isStreaming && (
                <ChatMessage 
                  message={{
                    id: 'streaming',
                    role: 'assistant',
                    content: streamingContent,
                    created_at: new Date().toISOString()
                  }}
                  isStreaming={true}
                />
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-0 z-30 p-4 md:p-6 lg:pb-8 bg-gradient-to-t from-background via-background to-transparent pt-20">
        <form 
          onSubmit={handleSubmit}
          className="relative mx-auto w-full max-w-3xl"
        >
          <div className="relative flex items-center gap-2 rounded-[24px] border border-border/60 bg-secondary/80 p-2 shadow-2xl backdrop-blur-xl transition-all duration-300 focus-within:border-primary/40 focus-within:ring-4 focus-within:ring-primary/10">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-transparent px-6 py-4 text-sm font-medium placeholder:text-muted-foreground/50 focus:outline-none"
              disabled={isStreaming}
            />
            <div className="flex items-center gap-1 pr-1">
               <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className={cn(
                  "flex h-11 w-11 items-center justify-center rounded-[18px] transition-all duration-300",
                  !input.trim() || isStreaming 
                    ? "bg-muted text-muted-foreground opacity-50 cursor-not-allowed" 
                    : "bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-105 active:scale-95 shadow-lg shadow-primary/25"
                )}
              >
                {isStreaming ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} className="ml-0.5" />}
              </button>
            </div>
          </div>
          <div className="mt-3 text-center text-[10px] text-muted-foreground/40 font-medium">
             AI-generated content may be inaccurate. Verify with citations.
          </div>
        </form>
      </div>
    </div>
  );
};

const ChatMessage = ({ message, isStreaming }: { message: Message, isStreaming?: boolean }) => {
  const isAssistant = message.role === 'assistant';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      layout
      className={cn(
        "flex w-full gap-5",
        isAssistant ? "justify-start" : "justify-end"
      )}
    >
      <div className={cn(
        "flex max-w-[85%] md:max-w-[75%] gap-4 rounded-3xl p-6 shadow-sm relative group transition-all",
        isAssistant 
          ? "glass-card text-foreground rounded-tl-sm border-l-4 border-l-primary/40" 
          : "bg-primary text-primary-foreground rounded-tr-sm shadow-primary/10"
      )}>
        
        <div className="flex flex-col space-y-4 overflow-hidden w-full">
          {/* Header for AI */}
          {isAssistant && (
             <div className="flex items-center gap-2 mb-1">
                <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10 text-primary">
                  <Sparkles size={12} />
                </div>
                <span className="text-xs font-bold text-primary">AI Copilot</span>
             </div>
          )}

          <div className="prose prose-sm dark:prose-invert max-w-none break-words whitespace-pre-wrap text-[14px] leading-7 tracking-wide font-normal">
            {message.content || (isStreaming ? <span className="inline-block h-4 w-1.5 animate-pulse bg-primary" /> : null)}
          </div>
          
          {isAssistant && message.citations && message.citations.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-4 mt-2 border-t border-border/40">
              {message.citations.map((citation, idx) => (
                <CitationItem key={`${citation.document_id}-${idx}`} citation={citation} index={idx + 1} />
              ))}
            </div>
          )}

          {isAssistant && !isStreaming && (
            <div className="flex items-center gap-4 pt-2 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground">
              <button className="flex items-center gap-1.5 hover:text-primary transition-colors">
                <Copy size={12} /> Copy
              </button>
              <button className="flex items-center gap-1.5 hover:text-primary transition-colors">
                <RefreshCcw size={12} /> Regenerate
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

const CitationItem = ({ citation, index }: { citation: any, index: number }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="flex items-center gap-1.5 rounded-full bg-primary/10 pl-2 pr-3 py-1 text-[10px] font-bold text-primary transition-all hover:bg-primary/20 hover:scale-105 border border-primary/10"
      >
        <Quote size={10} className="fill-current" />
        Source {index}
        <span className="opacity-50 font-normal">| {citation.filename}</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute bottom-full left-0 z-50 mb-3 w-80 overflow-hidden rounded-2xl border border-border bg-popover p-4 shadow-2xl dark:bg-zinc-900 ring-1 ring-white/10"
          >
            <div className="mb-3 flex items-center justify-between border-b border-border/50 pb-2">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-primary truncate max-w-[150px]">
                {citation.filename}
              </span>
              <span className="bg-secondary px-2 py-0.5 rounded text-[9px] font-bold text-muted-foreground border border-border/50">PAGE {citation.page}</span>
            </div>
            <div className="relative">
               <Quote size={12} className="absolute -top-1 -left-1 text-primary/20 rotate-180" />
               <p className="pl-4 text-[12px] leading-relaxed text-muted-foreground italic line-clamp-6 font-serif">
                {citation.chunk_text}
               </p>
            </div>
            
            <div className="mt-3 flex items-center justify-end">
               <span className="text-[9px] font-medium text-primary cursor-pointer hover:underline">Click to open PDF →</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
