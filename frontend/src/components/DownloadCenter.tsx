import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Download } from 'lucide-react';

interface DownloadCenterProps {
  sessionId: string | null;
  files: string[];
}

export function DownloadCenter({ sessionId, files }: DownloadCenterProps) {
  if (!sessionId) return null;

  const downloadFile = (filename: string) => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/download/${sessionId}/${filename}`;
  };

  return (
    <div className="p-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Download className="w-4 h-4" /> Downloads
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2 pb-3">
          {files.map(f => (
            <Button key={f} variant={f === 'package.zip' ? 'default' : 'outline'} size="sm" onClick={() => downloadFile(f)}>
              {f}
            </Button>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
