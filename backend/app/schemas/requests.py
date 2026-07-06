from pydantic import BaseModel, Field
from typing import Optional, List

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    
class ImproveRequest(BaseModel):
    dsl: str = Field(..., description="Existing Markdown DSL")
    prompt: Optional[str] = Field(None, description="Instructions on how to improve the DSL")

class GenerateResponse(BaseModel):
    message: str = Field(..., description="The AI's textual response")
    is_flow_generated: bool = Field(..., description="True if a flow was generated in this turn")
    session_id: Optional[str] = None
    dsl: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    files: Optional[List[str]] = None
