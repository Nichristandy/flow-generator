from pydantic import BaseModel, Field
from typing import Optional, List

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    provider: Optional[str] = Field("openrouter", description="The AI provider to use")
    model: Optional[str] = Field("deepseek/deepseek-coder", description="The specific model ID")
    api_key: Optional[str] = Field(None, description="API Key for the provider")
    mode: Optional[str] = Field("dsl", description="Generation mode: dsl or json")
    
class ImproveRequest(BaseModel):
    dsl: str = Field(..., description="Existing Markdown DSL")
    prompt: Optional[str] = Field(None, description="Instructions on how to improve the DSL")
    provider: Optional[str] = Field("openrouter", description="The AI provider to use")
    model: Optional[str] = Field("deepseek/deepseek-coder", description="The specific model ID")
    api_key: Optional[str] = Field(None, description="API Key for the provider")
    mode: Optional[str] = Field("dsl", description="Generation mode: dsl or json")

class RenderRequest(BaseModel):
    dsl: str = Field(..., description="Markdown DSL to render directly")

class GenerateResponse(BaseModel):
    message: str = Field(..., description="The AI's textual response")
    is_flow_generated: bool = Field(..., description="True if a flow was generated in this turn")
    session_id: Optional[str] = None
    dsl: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    files: Optional[List[str]] = None
