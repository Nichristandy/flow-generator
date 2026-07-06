"use client";

import { useState } from 'react';
import { ChatInterface } from '@/components/ChatInterface';
import { LivePreview } from '@/components/LivePreview';
import { MarkdownEditor } from '@/components/MarkdownEditor';
import { DownloadCenter } from '@/components/DownloadCenter';
import axios from 'axios';

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [history, setHistory] = useState<{role: string, content: string}[]>([
    { role: 'assistant', content: 'Hello! Describe the business process you want me to generate.' }
  ]);
  const [sessionInfo, setSessionInfo] = useState<{
    sessionId: string;
    dsl: string;
    previewUrl: string;
    files: string[];
  } | null>(null);

  const handleSendMessage = async (prompt: string) => {
    if (!prompt.trim() || isGenerating) return;
    
    const newHistory = [...history, { role: 'user', content: prompt }];
    setHistory(newHistory);
    setIsGenerating(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/chat', { messages: newHistory });
      
      setHistory(prev => [...prev, { role: 'assistant', content: response.data.message }]);
      
      if (response.data.is_flow_generated) {
        setSessionInfo({
          sessionId: response.data.session_id,
          dsl: response.data.dsl,
          previewUrl: response.data.preview_url,
          files: response.data.files
        });
      }
    } catch (error) {
      console.error("Generation failed:", error);
      alert("Failed to generate flow. Check console for details.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-white dark:bg-slate-950 overflow-hidden">
      {/* Sidebar Chat */}
      <div className="w-1/3 min-w-[300px] max-w-[400px] h-full flex-shrink-0">
        <ChatInterface 
          history={history}
          onSendMessage={handleSendMessage} 
          isGenerating={isGenerating} 
        />
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="flex-1 flex flex-col lg:flex-row min-h-0">
          <div className="flex-1 min-w-0">
            <LivePreview previewUrl={sessionInfo?.previewUrl || null} />
          </div>
          <div className="flex-1 min-w-0 lg:max-w-md">
            <MarkdownEditor dsl={sessionInfo?.dsl || null} />
          </div>
        </div>
        
        {/* Downloads fixed at bottom of main area */}
        <div className="flex-shrink-0">
          <DownloadCenter sessionId={sessionInfo?.sessionId || null} files={sessionInfo?.files || []} />
        </div>
      </div>
    </div>
  );
}
