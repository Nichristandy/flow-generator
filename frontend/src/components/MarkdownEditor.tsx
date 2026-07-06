import React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';

interface MarkdownEditorProps {
  dsl: string | null;
}

export function MarkdownEditor({ dsl }: MarkdownEditorProps) {
  return (
    <div className="flex-1 flex flex-col h-full border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 font-semibold text-lg">
        Markdown DSL
      </div>
      <ScrollArea className="flex-1 bg-slate-900 text-slate-100 p-4 font-mono text-sm">
        <pre>{dsl || "// Flow DSL will appear here"}</pre>
      </ScrollArea>
    </div>
  );
}
