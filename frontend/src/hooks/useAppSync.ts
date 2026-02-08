'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/useChatStore';
import { getDocumentStatus, listDocuments, listConversations } from '@/lib/api';

export function useAppSync() {
  const { 
    documents, 
    setDocuments, 
    updateDocumentStatus, 
    setLoadingDocuments,
    setConversations,
    setLoadingConversations
  } = useChatStore();
  
  const pollingInterval = useRef<NodeJS.Timeout | null>(null);

  // Initial load for docs and conversations
  useEffect(() => {
    const syncApp = async () => {
      setLoadingDocuments(true);
      setLoadingConversations(true);
      
      try {
        const [docsData, convsData] = await Promise.all([
          listDocuments(),
          listConversations()
        ]);
        
        const mappedDocs = (docsData || []).map((d: any) => ({
          ...d,
          status: d.processed ? 'ready' : (d.processing_error ? 'failed' : 'processing')
        }));
        
        setDocuments(mappedDocs);
        setConversations(convsData || []);
      } catch (err) {
        console.error('Failed to sync app data', err);
      } finally {
        setLoadingDocuments(false);
        setLoadingConversations(false);
      }
    };
    
    syncApp();
  }, [setDocuments, setLoadingDocuments, setConversations, setLoadingConversations]);

  // Polling for processing documents
  useEffect(() => {
    const processingDocs = documents.filter(doc => doc.status === 'processing');
    
    if (processingDocs.length > 0 && !pollingInterval.current) {
      pollingInterval.current = setInterval(async () => {
        for (const doc of processingDocs) {
          try {
            const status = await getDocumentStatus(doc.id);
            if (status && status.status !== 'processing') {
              updateDocumentStatus(doc.id, status.status);
            }
          } catch (err) {
            console.error(`Status check failed for ${doc.id}`, err);
          }
        }
      }, 3000);
    } else if (processingDocs.length === 0 && pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }

    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
    };
  }, [documents, updateDocumentStatus]);
}
