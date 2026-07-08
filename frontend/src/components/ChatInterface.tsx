import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2 } from 'lucide-react';

interface ChatInterfaceProps {
  history: {role: string, content: string}[];
  onSendMessage: (prompt: string) => void;
  isGenerating: boolean;
}

export function ChatInterface({ history, onSendMessage, isGenerating }: ChatInterfaceProps) {
  const [prompt, setPrompt] = useState("");

  const handleSend = () => {
    if (!prompt.trim() || isGenerating) return;
    onSendMessage(prompt);
    setPrompt("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 border-none">
      <div className="px-4 py-2 bg-slate-50 dark:bg-slate-950/50 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        Chat
      </div>
      
      <ScrollArea className="flex-1 p-4 min-h-0">
        <div className="flex flex-col gap-4">
          {history.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[85%] rounded-lg p-3 whitespace-pre-wrap ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isGenerating && (
            <div className="flex flex-col items-start">
              <div className="max-w-[85%] rounded-lg p-3 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <div className="flex gap-2 items-end">
          <Textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your process description... (Shift+Enter for new line)"
            onKeyDown={handleKeyDown}
            disabled={isGenerating}
            className="flex-1 min-h-[60px] max-h-[200px] resize-y text-sm"
          />
          <Button onClick={handleSend} disabled={isGenerating || !prompt.trim()} className="mb-1 bg-blue-600 hover:bg-blue-700">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
