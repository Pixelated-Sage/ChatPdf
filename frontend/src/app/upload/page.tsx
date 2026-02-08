'use client';

import { Sidebar } from '@/components/Sidebar';
import { DocumentUploader } from '@/components/DocumentUploader';
import { motion } from 'framer-motion';

export default function UploadPage() {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      
      <main className="flex-1 transition-all duration-300 sm:ml-72 w-full">
        <div className="flex h-screen flex-col items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12 text-center"
          >
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl text-balance">
              Knowledge Base
            </h1>
            <p className="mt-3 text-muted-foreground text-balance max-w-md mx-auto">
              Add your research papers, manuals, or contracts to start the conversation.
            </p>
          </motion.div>

          <DocumentUploader />
        </div>
      </main>
    </div>
  );
}
