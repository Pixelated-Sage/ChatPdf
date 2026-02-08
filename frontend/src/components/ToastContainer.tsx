'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToastStore } from '@/store/useToastStore';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export const ToastContainer = () => {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            layout
            initial={{ opacity: 0, x: 50, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
            className={cn(
              "pointer-events-auto flex w-80 items-start gap-3 overflow-hidden rounded-2xl border p-4 shadow-2xl glass",
              toast.type === 'success' && "border-emerald-500/20",
              toast.type === 'error' && "border-rose-500/20",
              toast.type === 'info' && "border-primary/20"
            )}
          >
            <div className={cn(
              "mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg",
              toast.type === 'success' && "bg-emerald-500/10 text-emerald-500",
              toast.type === 'error' && "bg-rose-500/10 text-rose-500",
              toast.type === 'info' && "bg-primary/10 text-primary"
            )}>
              {toast.type === 'success' && <CheckCircle2 size={16} />}
              {toast.type === 'error' && <AlertCircle size={16} />}
              {toast.type === 'info' && <Info size={16} />}
            </div>
            
            <div className="flex-1 text-sm font-medium leading-relaxed text-foreground">
              {toast.message}
            </div>

            <button 
              onClick={() => removeToast(toast.id)}
              className="text-foreground/20 hover:text-foreground transition-colors"
            >
              <X size={16} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
