import os
import httpx
from abc import ABC, abstractmethod
from typing import Optional

class AIProvider(ABC):
    @abstractmethod
    async def generate_dsl(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def improve_dsl(self, current_dsl: str, instructions: Optional[str]) -> str:
        pass
        
    @abstractmethod
    async def repair_dsl(self, dsl: str, error_message: str) -> str:
        pass

class OpenAICompatibleProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY")
        self.base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
        self.model = os.getenv("AI_MODEL", "deepseek-coder")
        
        if not self.api_key:
            print("WARNING: AI_API_KEY is not set.")
            
        self.system_prompt = """You are an expert Business Process Analyst.
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

    async def _call_api(self, messages: list) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            # Add OpenRouter specific headers if using OpenRouter
            if "openrouter" in self.base_url:
                headers["HTTP-Referer"] = "http://localhost:3000"
                headers["X-Title"] = "AI Flow Generator"
                
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
            if content.startswith("```markdown"):
                content = content[11:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            return content.strip()

    async def generate_dsl(self, conversation: list) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in conversation:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return await self._call_api(messages)

    async def improve_dsl(self, current_dsl: str, instructions: Optional[str]) -> str:
        prompt = "Improve the following Markdown DSL."
        if instructions:
            prompt += f" Instructions: {instructions}"
        prompt += f"\n\nExisting DSL:\n{current_dsl}"
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        return await self._call_api(messages)

    async def repair_dsl(self, dsl: str, error_message: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"The following DSL failed validation.\n\nDSL:\n{dsl}\n\nError:\n{error_message}\n\nPlease fix the DSL and return ONLY the corrected DSL."}
        ]
        return await self._call_api(messages)
