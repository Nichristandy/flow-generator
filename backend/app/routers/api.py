from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os

from app.schemas.requests import ChatRequest, ImproveRequest, RenderRequest, GenerateResponse
from app.services.pipeline import PipelineService, TEMP_DIR

router = APIRouter(prefix="/api", tags=["Flow Generator"])
pipeline = PipelineService()

@router.get("/config")
async def get_config():
    """Returns available models from env vars so frontend can populate dropdowns dynamically."""
    return {
        "openrouter_models": [m.strip() for m in os.getenv("OPENROUTER_MODELS", "deepseek/deepseek-coder").split(",")],
        "deepseek_models": [m.strip() for m in os.getenv("DEEPSEEK_MODELS", "deepseek-coder,deepseek-chat").split(",")]
    }

@router.post("/chat", response_model=GenerateResponse)
async def generate_flow(request: ChatRequest):
    try:
        # Convert ChatMessage objects to dicts
        conversation = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        response_dict = await pipeline.generate_flow(
            conversation,
            provider_name=request.provider,
            model=request.model,
            api_key=request.api_key
        )
        return GenerateResponse(**response_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improve", response_model=GenerateResponse)
async def improve_flow(request: ImproveRequest):
    try:
        response_dict = await pipeline.improve_flow(
            request.dsl, 
            request.prompt,
            provider_name=request.provider,
            model=request.model,
            api_key=request.api_key
        )
        return GenerateResponse(**response_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/render", response_model=GenerateResponse)
async def render_flow(request: RenderRequest):
    try:
        response_dict = await pipeline.render_flow(request.dsl)
        return GenerateResponse(**response_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    file_path = TEMP_DIR / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    media_type = "application/octet-stream"
    if filename.endswith(".svg"):
        media_type = "image/svg+xml"
    elif filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".zip"):
        media_type = "application/zip"
    elif filename.endswith(".md") or filename.endswith(".mmd") or filename.endswith(".puml"):
        media_type = "text/plain"
        
    return FileResponse(path=file_path, media_type=media_type, filename=filename)
