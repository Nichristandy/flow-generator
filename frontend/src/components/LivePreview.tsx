import React, { useEffect, useState, useMemo } from 'react';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

interface LivePreviewProps {
  previewUrl: string | null;
}

export function LivePreview({ previewUrl }: LivePreviewProps) {
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState<number>(0.8); // Default slightly zoomed out

  useEffect(() => {
    if (previewUrl && previewUrl.endsWith('.svg')) {
      fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + previewUrl)
        .then(res => {
          if (!res.ok) throw new Error("Failed to load preview");
          return res.text();
        })
        .then(text => {
          setSvgContent(text);
          setError(null);
        })
        .catch(err => {
          setError(err.message);
          setSvgContent(null);
        });
    } else {
      setSvgContent(null);
    }
  }, [previewUrl]);

  const zoomedSvg = useMemo(() => {
    if (!svgContent) return null;
    return svgContent.replace(/width="(\d+)"\s+height="(\d+)"/, (match, w, h) => {
      const newW = Math.round(parseInt(w) * zoom);
      const newH = Math.round(parseInt(h) * zoom);
      // We also need to add viewBox to ensure the internal coordinates scale correctly
      return `width="${newW}" height="${newH}" viewBox="0 0 ${w} ${h}"`;
    });
  }, [svgContent, zoom]);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.2));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 font-semibold text-lg flex items-center justify-between">
        <span>Live Preview</span>
        <div className="flex items-center gap-2">
          <button onClick={handleZoomOut} className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500" title="Zoom Out">
            <ZoomOut size={18} />
          </button>
          <span className="text-sm text-slate-400 w-12 text-center">{Math.round(zoom * 100)}%</span>
          <button onClick={handleZoomIn} className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500" title="Zoom In">
            <ZoomIn size={18} />
          </button>
          <button onClick={handleResetZoom} className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-500 ml-2" title="Reset Zoom">
            <Maximize size={18} />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-auto bg-slate-50 dark:bg-slate-900 p-4">
        {error ? (
          <div className="text-red-500 p-4">{error}</div>
        ) : zoomedSvg ? (
          <div 
            className="w-full h-full"
            dangerouslySetInnerHTML={{ __html: zoomedSvg }}
          />
        ) : previewUrl ? (
          <div className="text-slate-500 p-4">Loading preview...</div>
        ) : (
          <div className="text-slate-400 p-4">Generate a flow to see the preview here.</div>
        )}
      </div>
    </div>
  );
}
