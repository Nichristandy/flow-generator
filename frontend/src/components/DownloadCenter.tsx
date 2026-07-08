import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Download } from 'lucide-react';

interface DownloadCenterProps {
  sessionId: string | null;
  files: string[];
}

export function DownloadCenter({ sessionId, files }: DownloadCenterProps) {
  const downloadFile = (filename: string) => {
    if (!sessionId) return;
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/download/${sessionId}/${filename}`;
  };

  return (
    <div className="p-3 bg-slate-50 dark:bg-slate-900 flex items-center justify-between">
      <div className="text-sm font-medium flex items-center gap-2 text-slate-600 dark:text-slate-400">
        <Download className="w-4 h-4" /> Downloads
      </div>
      <div className="flex flex-wrap gap-2">
        {!sessionId ? (
          <span className="text-sm text-slate-400">Generate a flow to enable downloads</span>
        ) : (
          files.map(f => (
            <Button key={f} variant={f === 'package.zip' ? 'default' : 'outline'} size="sm" onClick={() => downloadFile(f)} className="h-8 text-xs">
              {f}
            </Button>
          ))
        )}
      </div>
    </div>
  );
}
