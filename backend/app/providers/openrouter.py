import os
import httpx
from typing import Optional, List, Dict
from app.providers.base import AIProvider

class OpenRouterProvider(AIProvider):
    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key, model)
        # Fallback to env vars if not explicitly provided
        self.api_key = self.api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("AI_API_KEY")
        self.model = self.model or os.getenv("AI_MODEL", "deepseek/deepseek-coder")
        self.base_url = "https://openrouter.ai/api/v1"
        
        self.dsl_system_prompt = """You are an expert Business Process Analyst.
Your goal is to help the user design a complete business process flow and eventually output a strict custom Markdown DSL.
Do NOT generate Mermaid, BPMN XML, or Draw.io XML. ONLY generate the Markdown DSL.

PROCESS DEFINITION:
1. When the user provides a process description, review it for completeness.
2. If there are ambiguous steps, missing actors, or missing outcomes for conditional branches (e.g., they say "If approved, do X" but don't say what happens if rejected), ask clarifying questions! 
3. Only ask 1-2 questions at a time. Be conversational and helpful.
4. If the process is fully defined, generate the Markdown DSL and wrap it EXACTLY in `<dsl>` and `</dsl>` tags.

STRICT DSL SYNTAX RULES:
1. The flow MUST start with `Start` and end with `End` on their own lines.
2. Tasks MUST be written EXACTLY as `Actor: Task Description` (e.g., `Requester: Submit Form`). Do NOT use bullet points, bold text, or Markdown inside the DSL.
3. Conditions use `IF Condition` (no colons), followed by indented tasks, optionally an `ELSE` line, and MUST close with `ENDIF`.
4. Indentation (exactly 4 spaces) is STRICTLY REQUIRED inside `IF`, `ELSE`, and `PARALLEL` blocks.
5. DO NOT invent random `LABEL` tags. ONLY use `LABEL LoopName` and `GOTO LoopName` if the user explicitly describes a loop (e.g., "goes back to the beginning"). 
6. Keep task descriptions concise.

Example of a PERFECT output:
<dsl>
Start
Requester: Create Material Request
IF Request is valid
    Manager: Approve Request
ELSE
    System: Reject Request
    GOTO End Process
ENDIF
LABEL End Process
End
</dsl>
"""

        self.json_system_prompt = """You are an expert Business Process Analyst.
Your goal is to help the user design a complete business process flow and eventually output a strict JSON array.
Do NOT generate Mermaid, BPMN XML, or Draw.io XML. ONLY generate the JSON array.

PROCESS DEFINITION:
1. When the user provides a process description, review it for completeness.
2. If there are ambiguous steps, missing actors, or missing outcomes for conditional branches (e.g., they say "If approved, do X" but don't say what happens if rejected), ask clarifying questions! 
3. Only ask 1-2 questions at a time. Be conversational and helpful.
4. If the process is fully defined, generate the JSON array and wrap it EXACTLY in `<json>` and `</json>` tags.

STRICT JSON SYNTAX RULES:
The output must be a valid JSON array of objects. Each object represents a step in the flow.
Valid types:
- {"type": "start"}
- {"type": "task", "actor": "Role", "action": "Task description"}
- {"type": "if", "condition": "Condition description"}
- {"type": "else"}
- {"type": "endif"}
- {"type": "label", "name": "LoopName"}
- {"type": "goto", "target": "LoopName"}
- {"type": "end"}

Example:
<json>
[
  {"type": "start"},
  {"type": "task", "actor": "Requester", "action": "Submit Form"},
  {"type": "if", "condition": "Is Valid?"},
  {"type": "task", "actor": "Manager", "action": "Approve"},
  {"type": "else"},
  {"type": "task", "actor": "System", "action": "Reject"},
  {"type": "endif"},
  {"type": "end"}
]
</json>
"""

    def _get_prompt(self, mode: str) -> str:
        return self.json_system_prompt if mode == "json" else self.dsl_system_prompt

    async def _call_api(self, messages: list) -> str:
        if not self.api_key:
            return "Error: API Key is required for OpenRouter."
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Flow Generator"
            }
                
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            # Clean up potential markdown blocks the model might incorrectly add
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```markdown"):
                content = content[11:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            return content.strip()

    async def generate_dsl(self, conversation: List[Dict[str, str]], mode: str = "dsl") -> str:
        messages = [{"role": "system", "content": self._get_prompt(mode)}]
        for msg in conversation:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return await self._call_api(messages)

    async def improve_dsl(self, current_dsl: str, instructions: Optional[str], mode: str = "dsl") -> str:
        prompt = "Improve the following definition."
        if instructions:
            prompt += f" Instructions: {instructions}"
        prompt += f"\n\nExisting definition:\n{current_dsl}"
        
        messages = [
            {"role": "system", "content": self._get_prompt(mode)},
            {"role": "user", "content": prompt}
        ]
        return await self._call_api(messages)

    async def repair_dsl(self, dsl: str, error_message: str, mode: str = "dsl") -> str:
        messages = [
            {"role": "system", "content": self._get_prompt(mode)},
            {"role": "user", "content": f"The following definition failed validation.\n\nDefinition:\n{dsl}\n\nError:\n{error_message}\n\nPlease fix it and return ONLY the corrected definition."}
        ]
        return await self._call_api(messages)
