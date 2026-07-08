import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Play } from 'lucide-react';

interface MarkdownEditorProps {
  dsl: string | null;
  onRender?: (dsl: string) => void;
  isGenerating?: boolean;
}

export function MarkdownEditor({ dsl, onRender, isGenerating }: MarkdownEditorProps) {
  const [localDsl, setLocalDsl] = useState("");

  useEffect(() => {
    if (dsl) setLocalDsl(dsl);
  }, [dsl]);

  return (
    <div className="flex-1 flex flex-col h-full border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 font-semibold text-lg flex items-center justify-between">
        <span>Markdown DSL</span>
        {onRender && (
          <Button 
            size="sm" 
            onClick={() => onRender(localDsl)} 
            disabled={isGenerating || !localDsl.trim() || localDsl === dsl}
            className="flex items-center gap-1"
          >
            <Play className="w-3 h-3" /> Update Flow
          </Button>
        )}
      </div>
      <div className="flex-1 bg-slate-900 p-4">
        <Textarea 
          value={localDsl}
          onChange={(e) => setLocalDsl(e.target.value)}
          placeholder="// Flow DSL will appear here"
          className="w-full h-full bg-slate-900 text-slate-100 font-mono text-sm border-none focus-visible:ring-0 focus-visible:ring-offset-0 p-0 resize-none"
          spellCheck={false}
        />
      </div>
    </div>
  );
}
