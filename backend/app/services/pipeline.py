import uuid
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from fastapi import HTTPException

from app.providers import get_provider
from app.generator.parser.flow_parser import FlowParser
from app.generator.parser.flow_json_parser import FlowJsonParser
from app.generator.graph.compiler import AstCompiler
from app.generator.layout.layout_engine import LayoutEngine
from app.generator.layout.preview_renderer import PreviewRenderer
from app.generator.generators.mermaid import MermaidGenerator
from app.generator.generators.bpmn import BpmnGenerator
from app.generator.generators.drawio import DrawioGenerator
from app.generator.generators.plantuml import PlantUmlGenerator
from app.generator.exporters.graphviz_exporter import GraphvizExporter

MAX_REPAIRS = 3
TEMP_DIR = Path("temp")

class PipelineService:
    def __init__(self):
        pass

    async def generate_flow(self, conversation: List[dict], provider_name: str = None, model: str = None, api_key: str = None, mode: str = "dsl") -> dict:
        provider = get_provider(provider_name, api_key, model)
        
        # 1. Get AI response
        ai_response = await provider.generate_dsl(conversation, mode=mode)
        
        # 2. Extract content based on mode
        tag = "<json>" if mode == "json" else "<dsl>"
        end_tag = "</json>" if mode == "json" else "</dsl>"
        
        if tag in ai_response and end_tag in ai_response:
            start = ai_response.find(tag) + len(tag)
            end = ai_response.find(end_tag)
            content = ai_response[start:end].strip()
            
            message = ai_response.replace(ai_response[start-len(tag):end+len(end_tag)], "").strip()
            if not message:
                message = "Flow generated successfully!"
                
            content = await self._validate_and_repair(content, provider, mode)
            session_id, processed_content, generated_files = self._process_content(content, mode)
            
            return {
                "message": message,
                "is_flow_generated": True,
                "session_id": session_id,
                "dsl": processed_content,
                "preview_url": f"/api/download/{session_id}/process.svg",
                "download_url": f"/api/download/{session_id}/package.zip",
                "files": generated_files
            }
        else:
            return {
                "message": ai_response,
                "is_flow_generated": False
            }

    async def improve_flow(self, dsl: str, prompt: Optional[str] = None, provider_name: str = None, model: str = None, api_key: str = None, mode: str = "dsl") -> dict:
        provider = get_provider(provider_name, api_key, model)
        improved = await provider.improve_dsl(dsl, prompt, mode=mode)
        
        tag = "<json>" if mode == "json" else "<dsl>"
        end_tag = "</json>" if mode == "json" else "</dsl>"
        
        if tag in improved and end_tag in improved:
            start = improved.find(tag) + len(tag)
            end = improved.find(end_tag)
            improved = improved[start:end].strip()
            
        improved = await self._validate_and_repair(improved, provider, mode)
        session_id, processed, generated_files = self._process_content(improved, mode)
        
        return {
            "message": "Flow updated successfully!",
            "is_flow_generated": True,
            "session_id": session_id,
            "dsl": processed,
            "preview_url": f"/api/download/{session_id}/process.svg",
            "download_url": f"/api/download/{session_id}/package.zip",
            "files": generated_files
        }

    async def render_flow(self, dsl: str, mode: str = "dsl") -> dict:
        try:
            # We skip repair for manual render
            parser = FlowJsonParser() if mode == "json" else FlowParser()
            ast = parser.parse(dsl)
            compiler = AstCompiler(ast)
            compiler.compile()
            
            session_id, processed, generated_files = self._process_content(dsl, mode)
            
            return {
                "message": "Flow rendered successfully!",
                "is_flow_generated": True,
                "session_id": session_id,
                "dsl": processed,
                "preview_url": f"/api/download/{session_id}/process.svg",
                "download_url": f"/api/download/{session_id}/package.zip",
                "files": generated_files
            }
        except Exception as e:
            return {
                "message": f"Failed to render: {str(e)}",
                "is_flow_generated": False
            }

    async def _validate_and_repair(self, content: str, provider, mode: str) -> str:
        parser = FlowJsonParser() if mode == "json" else FlowParser()
        
        for _ in range(MAX_REPAIRS):
            try:
                ast = parser.parse(content)
                compiler = AstCompiler(ast)
                compiler.compile()
                return content
            except Exception as e:
                error_message = str(e)
                print(f"Validation failed: {error_message}. Attempting repair...")
                content = await provider.repair_dsl(content, error_message, mode=mode)
                
        raise HTTPException(status_code=500, detail="Failed to generate valid flow after multiple repair attempts.")

    def _process_content(self, content: str, mode: str) -> Tuple[str, str, List[str]]:
        session_id = str(uuid.uuid4())
        session_dir = TEMP_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            parser = FlowJsonParser() if mode == "json" else FlowParser()
            ast = parser.parse(content)
            compiler = AstCompiler(ast)
            builder = compiler.compile()
            
            engine = LayoutEngine(builder)
            engine.execute()
            
            generated_files = []
            
            if mode == "json":
                (session_dir / "process.json").write_text(content)
                generated_files.append("process.json")
            else:
                (session_dir / "process.md").write_text(content)
                generated_files.append("process.md")
            
            renderer = PreviewRenderer(builder, engine.nodes, engine.edges)
            svg_content = renderer.render_svg()
            (session_dir / "process.svg").write_text(svg_content)
            generated_files.append("process.svg")
            
            mermaid_gen = MermaidGenerator()
            (session_dir / "process.mmd").write_text(mermaid_gen.generate(builder))
            generated_files.append("process.mmd")
            
            bpmn_gen = BpmnGenerator()
            (session_dir / "process.bpmn").write_text(bpmn_gen.generate(builder))
            generated_files.append("process.bpmn")
            
            drawio_gen = DrawioGenerator()
            (session_dir / "process.drawio").write_text(drawio_gen.generate(builder))
            generated_files.append("process.drawio")
            
            puml_gen = PlantUmlGenerator()
            (session_dir / "process.puml").write_text(puml_gen.generate(builder))
            generated_files.append("process.puml")
            
            zip_path = session_dir / "package"
            shutil.make_archive(str(zip_path), 'zip', str(session_dir))
            generated_files.append("package.zip")
            
            return session_id, content, generated_files
            
        except Exception as e:
            if session_dir.exists():
                shutil.rmtree(session_dir)
            raise HTTPException(status_code=500, detail=f"Flow generation failed: {str(e)}")
