import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple, List, Optional
from fastapi import HTTPException

from app.ai.provider import AIProvider, OpenAICompatibleProvider
from app.generator.parser.flow_parser import FlowParser
from app.generator.validator.validator import AstValidator
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
        self.ai_provider: AIProvider = OpenAICompatibleProvider()

    async def generate_flow(self, conversation: List[dict]) -> dict:
        """Generates flow from prompt, validates it, and generates all files."""
        # 1. Get AI response
        ai_response = await self.ai_provider.generate_dsl(conversation)
        
        # 2. Check if DSL was generated
        if "<dsl>" in ai_response and "</dsl>" in ai_response:
            start = ai_response.find("<dsl>") + 5
            end = ai_response.find("</dsl>")
            dsl = ai_response[start:end].strip()
            
            # Clean up message for user
            message = ai_response.replace(ai_response[start-5:end+6], "").strip()
            if not message:
                message = "Flow generated successfully!"
                
            dsl = await self._validate_and_repair(dsl)
            session_id, processed_dsl, generated_files = self._process_dsl(dsl)
            
            return {
                "message": message,
                "is_flow_generated": True,
                "session_id": session_id,
                "dsl": processed_dsl,
                "preview_url": f"/api/download/{session_id}/process.svg",
                "download_url": f"/api/download/{session_id}/package.zip",
                "files": generated_files
            }
        else:
            return {
                "message": ai_response,
                "is_flow_generated": False
            }

    async def improve_flow(self, dsl: str, prompt: Optional[str] = None) -> dict:
        """Improves existing DSL."""
        improved_dsl = await self.ai_provider.improve_dsl(dsl, prompt)
        
        if "<dsl>" in improved_dsl and "</dsl>" in improved_dsl:
            start = improved_dsl.find("<dsl>") + 5
            end = improved_dsl.find("</dsl>")
            improved_dsl = improved_dsl[start:end].strip()
            
        improved_dsl = await self._validate_and_repair(improved_dsl)
        session_id, processed_dsl, generated_files = self._process_dsl(improved_dsl)
        
        return {
            "message": "Flow updated successfully!",
            "is_flow_generated": True,
            "session_id": session_id,
            "dsl": processed_dsl,
            "preview_url": f"/api/download/{session_id}/process.svg",
            "download_url": f"/api/download/{session_id}/package.zip",
            "files": generated_files
        }

    async def _validate_and_repair(self, dsl: str) -> str:
        parser = FlowParser()
        
        for _ in range(MAX_REPAIRS):
            try:
                # Try to parse
                ast = parser.parse(dsl)
                
                # Try to validate
                validator = AstValidator(ast)
                validator.validate()
                
                # If we got here, it's valid
                return dsl
            except Exception as e:
                error_message = str(e)
                print(f"Validation failed: {error_message}. Attempting repair...")
                dsl = await self.ai_provider.repair_dsl(dsl, error_message)
                
        # If we failed after max repairs, raise an exception
        raise HTTPException(status_code=500, detail="Failed to generate valid DSL after multiple repair attempts.")

    def _process_dsl(self, dsl: str) -> Tuple[str, str, List[str]]:
        """Runs the python generator, saves files to temp, zips them, and returns (session_id, dsl, files)"""
        session_id = str(uuid.uuid4())
        session_dir = TEMP_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Parse and Compile
            parser = FlowParser()
            ast = parser.parse(dsl)
            compiler = AstCompiler(ast)
            builder = compiler.compile()
            
            # Layout
            engine = LayoutEngine(builder)
            engine.execute()
            
            # Generate Text Formats
            generated_files = []
            
            # Save original DSL
            process_md = session_dir / "process.md"
            process_md.write_text(dsl)
            generated_files.append("process.md")
            
            # Custom Native SVG Preview
            renderer = PreviewRenderer(builder, engine.nodes, engine.edges)
            svg_content = renderer.render_svg()
            (session_dir / "process.svg").write_text(svg_content)
            generated_files.append("process.svg")
            
            # Mermaid
            mermaid_gen = MermaidGenerator()
            mermaid_content = mermaid_gen.generate(builder)
            (session_dir / "process.mmd").write_text(mermaid_content)
            generated_files.append("process.mmd")
            
            # BPMN
            bpmn_gen = BpmnGenerator()
            bpmn_content = bpmn_gen.generate(builder)
            (session_dir / "process.bpmn").write_text(bpmn_content)
            generated_files.append("process.bpmn")
            
            # Draw.io
            drawio_gen = DrawioGenerator()
            drawio_content = drawio_gen.generate(builder)
            (session_dir / "process.drawio").write_text(drawio_content)
            generated_files.append("process.drawio")
            
            # PlantUML
            puml_gen = PlantUmlGenerator()
            puml_content = puml_gen.generate(builder)
            (session_dir / "process.puml").write_text(puml_content)
            generated_files.append("process.puml")
            
            # Graphviz (SVG, PNG, PDF)
            try:
                exporter = GraphvizExporter(builder)
                exporter.export_png(str(session_dir / "process"))
                generated_files.append("process.png")
                exporter.export_pdf(str(session_dir / "process"))
                generated_files.append("process.pdf")
            except Exception as e:
                print(f"Warning: Graphviz export failed: {e}")
                
            # Create ZIP package
            zip_path = session_dir / "package"
            shutil.make_archive(str(zip_path), 'zip', str(session_dir))
            generated_files.append("package.zip")
            
            return session_id, dsl, generated_files
            
        except Exception as e:
            # Clean up if something fails critically
            if session_dir.exists():
                shutil.rmtree(session_dir)
            raise HTTPException(status_code=500, detail=f"Flow generation failed: {str(e)}")
