'use client';

import { Sidebar } from '@/components/Sidebar';
import { ChatInterface } from '@/components/ChatInterface';

export default function ChatPage() {
  return (
    <div className="flex bg-background h-screen overflow-hidden">
      <Sidebar />
      
      {/* 
        Sidebar is fixed width (w-72 = 18rem). 
        On mobile, main takes full width (flex-1).
        On desktop (sm), main pushes over by 18rem (sm:ml-72).
      */}
      <main className="flex-1 sm:ml-72 h-full w-full relative">
        <ChatInterface />
      </main>
    </div>
  );
}
