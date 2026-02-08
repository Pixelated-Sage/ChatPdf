'use client';

import { useAppSync } from '@/hooks/useAppSync';
import { ToastContainer } from '@/components/ToastContainer';

export function Providers({ children }: { children: React.ReactNode }) {
  useAppSync();
  return (
    <>
      {children}
      <ToastContainer />
    </>
  );
}
