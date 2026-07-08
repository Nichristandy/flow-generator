"use client";

import { useState } from 'react';
import { ProviderSettings, ProviderConfig } from '@/components/ProviderSettings';
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

  const [providerConfig, setProviderConfig] = useState<ProviderConfig>({
    provider: 'openrouter',
    model: 'deepseek/deepseek-coder',
    apiKey: '', // Not exposed in UI anymore, will fallback to env vars
    mode: 'dsl'
  });

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
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat`, { 
        messages: newHistory,
        provider: providerConfig.provider,
        model: providerConfig.model,
        api_key: providerConfig.apiKey,
        mode: providerConfig.mode
      });
      
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

  const handleRenderDSL = async (newDsl: string) => {
    if (!newDsl.trim() || isGenerating) return;
    
    setIsGenerating(true);
    
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/render`, { dsl: newDsl });
      
      if (response.data.is_flow_generated) {
        setSessionInfo(prev => prev ? {
          ...prev,
          sessionId: response.data.session_id,
          dsl: response.data.dsl,
          previewUrl: response.data.preview_url,
          files: response.data.files
        } : null);
      } else {
        alert("Failed to parse DSL: " + response.data.message);
      }
    } catch (error) {
      console.error("Render failed:", error);
      alert("Failed to render flow. Check console for details.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-50 dark:bg-slate-950 overflow-hidden font-sans">
      
      {/* LEFT SIDEBAR: Provider Settings + Chat */}
      <div className="w-[350px] flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800">
          <h1 className="font-bold text-lg text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center text-white text-xs">F</div>
            Flow Builder
          </h1>
        </div>
        
        {/* Settings (Top) */}
        <div className="border-b border-slate-200 dark:border-slate-800 max-h-[200px] overflow-y-auto">
          <ProviderSettings config={providerConfig} onChange={setProviderConfig} />
        </div>
        
        {/* Chat (Bottom) */}
        <div className="flex-1 min-h-0">
          <ChatInterface 
            history={history}
            onSendMessage={handleSendMessage} 
            isGenerating={isGenerating} 
          />
        </div>
      </div>
      
      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        
        <div className="flex-1 flex flex-col lg:flex-row min-h-0 bg-slate-100 dark:bg-slate-950">
          
          {/* Left/Top: Live Preview */}
          <div className="flex-1 flex flex-col min-w-0 border-b lg:border-b-0 lg:border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 m-2 rounded-xl shadow-sm overflow-hidden">
            <LivePreview previewUrl={sessionInfo?.previewUrl || null} />
          </div>
          
          {/* Right/Bottom: DSL Editor */}
          {providerConfig.mode === 'dsl' && (
            <div className="w-full lg:w-[450px] flex flex-col min-w-0 bg-white dark:bg-slate-900 m-2 ml-0 lg:mt-2 rounded-xl shadow-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 font-semibold text-lg flex items-center justify-between">
                <span>Markdown DSL</span>
              </div>
              <div className="flex-1 relative p-2">
                <MarkdownEditor 
                  dsl={sessionInfo?.dsl || null} 
                  onRender={handleRenderDSL}
                  isGenerating={isGenerating}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Downloads Strip */}
        <div className="flex-shrink-0 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 z-10 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
          <DownloadCenter sessionId={sessionInfo?.sessionId || null} files={sessionInfo?.files || []} />
        </div>
      </div>
      
    </div>
  );
}
