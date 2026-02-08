'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle2, AlertCircle, Loader2, MessageSquare, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { uploadDocument } from '@/lib/api';
import { useChatStore } from '@/store/useChatStore';
import { useToastStore } from '@/store/useToastStore';

export const DocumentUploader = () => {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const addDocument = useChatStore((state) => state.addDocument);
  const addToast = useToastStore((state) => state.addToast);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
    setError(null);
    setIsSuccess(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      for (const file of files) {
        const result = await uploadDocument(file);
        addDocument({
          id: result.document_id,
          filename: result.document_id + ".pdf",
          original_filename: file.name,
          status: 'processing',
          upload_date: new Date().toISOString(),
        });
      }
      setIsSuccess(true);
      addToast(`Successfully uploaded ${files.length} document(s)`, 'success');
      setFiles([]);
    } catch (err: any) {
      const msg = err.message || 'Failed to upload documents';
      setError(msg);
      addToast(msg, 'error');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-2xl">
      <AnimatePresence mode="wait">
        {!isSuccess ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            {/* Glass Card Dropzone */}
            <div 
              {...getRootProps()} 
              className={cn(
                "relative overflow-hidden rounded-3xl border border-dashed p-16 transition-all duration-500 glass-card",
                isDragActive 
                  ? "border-primary bg-primary/5 ring-2 ring-primary/20 scale-[1.01]" 
                  : "border-border/60 hover:border-primary/30 hover:bg-accent/30"
              )}
            >
              <input {...getInputProps()} />
              
              <div className="flex flex-col items-center justify-center space-y-8">
                <div className={cn(
                  "relative flex h-24 w-24 items-center justify-center rounded-3xl bg-secondary transition-all duration-500 shadow-inner",
                  isDragActive && "rotate-6 scale-110 shadow-lg shadow-primary/20"
                )}>
                  <Upload size={40} className={cn("text-muted-foreground transition-colors", isDragActive && "text-primary")} />
                  {isDragActive && (
                    <motion.div 
                      layoutId="upload-glow"
                      className="absolute inset-0 rounded-3xl bg-primary/10 blur-xl" 
                    />
                  )}
                </div>
                
                <div className="text-center space-y-3">
                  <h3 className="text-2xl font-bold tracking-tight text-foreground">
                    {isDragActive ? "Drop files now" : "Upload Research Papers"}
                  </h3>
                  <p className="mx-auto text-sm font-medium text-muted-foreground max-w-[300px] leading-relaxed">
                    Support for PDF documents up to 10MB. 
                    <br />
                    Drag & drop or click to browse.
                  </p>
                </div>

                <div className="rounded-xl bg-primary px-8 py-3 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-transform hover:scale-105 active:scale-95 cursor-pointer">
                  Browse Files
                </div>
              </div>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 space-y-4"
              >
                <div className="flex items-center justify-between px-2">
                  <h4 className="text-[10px] font-extrabold uppercase tracking-widest text-muted-foreground/70">
                    Workspace ({files.length})
                  </h4>
                </div>

                <div className="max-h-60 overflow-y-auto pr-2 space-y-2 thin-scrollbar">
                  {files.map((file, idx) => (
                    <motion.div 
                      key={`${file.name}-${idx}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="group flex items-center gap-4 rounded-xl border border-border/40 bg-card/50 p-3 backdrop-blur-sm transition-colors hover:border-border/80 hover:bg-card"
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-primary/80 ring-1 ring-white/5">
                        <FileText size={20} />
                      </div>
                      <div className="flex flex-1 flex-col overflow-hidden">
                        <span className="truncate text-sm font-semibold text-foreground">{file.name}</span>
                        <span className="text-[10px] text-muted-foreground mono">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                      </div>
                      <button 
                        onClick={() => removeFile(idx)}
                        className="p-2 text-muted-foreground/50 hover:text-destructive transition-colors"
                      >
                        <X size={18} />
                      </button>
                    </motion.div>
                  ))
                }
                </div>

                {error && (
                  <div className="flex items-center gap-3 rounded-xl bg-rose-500/10 p-4 text-xs font-semibold text-rose-500 border border-rose-500/20">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}

                <button
                  disabled={isUploading}
                  onClick={handleUpload}
                  className={cn(
                    "relative w-full overflow-hidden rounded-xl py-4 text-sm font-bold transition-all duration-300",
                    isUploading 
                      ? "bg-primary/50 cursor-not-allowed" 
                      : "bg-primary text-primary-foreground shadow-xl shadow-primary/20 hover:shadow-primary/30 active:scale-[0.98]"
                  )}
                >
                  <span className="relative z-10 flex items-center justify-center gap-2">
                    {isUploading ? (
                      <>
                        <Loader2 size={18} className="animate-spin" />
                        Indexing Knowledge Base...
                      </>
                    ) : (
                      <>
                        Start Processing
                        <ArrowRight size={18} />
                      </>
                    )}
                  </span>
                </button>
              </motion.div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center rounded-3xl border border-emerald-500/20 bg-emerald-500/5 p-12 text-center shadow-2xl backdrop-blur-sm"
          >
            <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-500 text-white shadow-xl shadow-emerald-500/20">
              <CheckCircle2 size={40} />
            </div>
            <h3 className="text-2xl font-bold tracking-tight text-foreground">Docs Indexed!</h3>
            <p className="mt-2 text-sm text-muted-foreground max-w-[280px]">
              Your research material is ready for querying.
            </p>
            <div className="mt-8 flex w-full flex-col gap-3">
              <button
                onClick={() => router.push('/chat')}
                className="flex items-center justify-center gap-2 rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95"
              >
                <MessageSquare size={18} />
                Open Chat
              </button>
              <button
                onClick={() => setIsSuccess(false)}
                className="rounded-xl border border-border bg-transparent py-3 text-sm font-bold text-muted-foreground transition-all hover:text-foreground hover:bg-secondary"
              >
                Upload More
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
