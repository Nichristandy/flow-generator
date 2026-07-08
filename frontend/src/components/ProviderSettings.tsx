import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import axios from "axios";

export interface ProviderConfig {
  provider: string;
  model: string;
  apiKey: string;
  mode: 'dsl' | 'json';
}

interface ProviderSettingsProps {
  config: ProviderConfig;
  onChange: (config: ProviderConfig) => void;
}

export function ProviderSettings({ config, onChange }: ProviderSettingsProps) {
  const [openRouterModels, setOpenRouterModels] = useState<{value: string, label: string}[]>([]);
  const [deepseekModels, setDeepseekModels] = useState<{value: string, label: string}[]>([]);

  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/config`);
        
        setOpenRouterModels(
          response.data.openrouter_models.map((m: string) => ({ value: m, label: m }))
        );
        setDeepseekModels(
          response.data.deepseek_models.map((m: string) => ({ value: m, label: m }))
        );
        
        // If current model is empty, set default
        if (!config.model) {
          onChange({
            ...config,
            model: config.provider === 'deepseek' ? response.data.deepseek_models[0] : response.data.openrouter_models[0]
          });
        }
      } catch (e) {
        console.error("Failed to fetch config", e);
      }
    }
    fetchConfig();
  }, []);

  const models = config.provider === 'deepseek' ? deepseekModels : openRouterModels;

  const handleProviderChange = (newProvider: string) => {
    const defaultModel = newProvider === 'deepseek' 
        ? (deepseekModels[0]?.value || 'deepseek-coder')
        : (openRouterModels[0]?.value || 'deepseek/deepseek-coder');
    onChange({ ...config, provider: newProvider, model: defaultModel });
  };

  return (
    <Card className="w-full border-none shadow-none bg-transparent">
      <CardHeader className="px-4 py-3">
        <CardTitle className="text-sm font-medium uppercase tracking-wider text-slate-500">Settings</CardTitle>
      </CardHeader>
      <CardContent className="px-4 space-y-4">
        <div className="space-y-2">
          <Label className="text-xs">Provider</Label>
          <select 
            className="flex h-8 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-xs shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            value={config.provider} 
            onChange={(e) => handleProviderChange(e.target.value)}
          >
            <option value="openrouter">OpenRouter</option>
            <option value="deepseek">DeepSeek (Direct)</option>
          </select>
        </div>

        <div className="space-y-2">
          <Label className="text-xs">Model</Label>
          <select 
            className="flex h-8 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-xs shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            value={config.model} 
            onChange={(e) => onChange({ ...config, model: e.target.value })}
          >
            {models.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label className="text-xs">Generation Mode</Label>
          <select 
            className="flex h-8 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-xs shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            value={config.mode} 
            onChange={(e) => onChange({ ...config, mode: e.target.value as 'dsl' | 'json' })}
          >
            <option value="dsl">Markdown DSL (Editable)</option>
            <option value="json">AI Direct Flow (No DSL)</option>
          </select>
        </div>
      </CardContent>
    </Card>
  );
}
