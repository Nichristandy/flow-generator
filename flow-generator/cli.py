import typer
from rich.console import Console
from pathlib import Path

from parser.yaml_parser import YamlParser
from parser.flow_parser import FlowParser
from validator.validator import AstValidator
from graph.compiler import AstCompiler
from layout.optimizer import LayoutOptimizer
from layout.connector import ConnectorOptimizer
from generators.mermaid import MermaidGenerator
from generators.bpmn import BpmnGenerator
from generators.drawio import DrawioGenerator
from generators.plantuml import PlantUmlGenerator
from exporters.graphviz_exporter import GraphvizExporter
from graphviz.backend.execute import ExecutableNotFound

app = typer.Typer(help="AI Flow Generator CLI")
console = Console()

@app.command()
def generate(
    input_file: Path = typer.Argument(..., help="Path to input file (.md, .yaml, .flow)"),
    format: str = typer.Option("all", help="Output format: mermaid, bpmn, drawio, plantuml, svg, png, pdf, or all"),
    layout: str = typer.Option("horizontal", help="Layout direction: horizontal or vertical"),
    output: Path = typer.Option(Path("output"), help="Output directory")
):
    """
    Generate multiple diagram formats from a simple business process description.
    """
    if not input_file.exists():
        console.print(f"[red]Error: File {input_file} not found.[/red]")
        raise typer.Exit(code=1)
        
    output.mkdir(parents=True, exist_ok=True)
    content = input_file.read_text()
    ext = input_file.suffix.lower()
    
    # 1. Parse
    console.print(f"Parsing {input_file.name}...")
    if ext in ['.yaml', '.yml']:
        parser = YamlParser()
    else:
        parser = FlowParser()
        
    ast = parser.parse(content)
    
    # 2. Validate
    console.print("Validating model...")
    validator = AstValidator(ast)
    try:
        validator.validate()
    except Exception as e:
        console.print(f"[red]Validation Error: {e}[/red]")
        raise typer.Exit(code=1)
        
    # 3. Compile AST to Graph
    console.print("Compiling AST to Graph...")
    compiler = AstCompiler(ast)
    builder = compiler.compile()
        
    # 4. Layout Engine
    console.print("Applying auto-layout...")
    optimizer = LayoutOptimizer(builder)
    optimizer.optimize()
    connector = ConnectorOptimizer(builder)
    connector.optimize()
    
    # 5. Generate & Export
    base_name = input_file.stem
    console.print("\n[bold green]Generating outputs:[/bold green]")
    
    generated = []
    
    def save_text(ext_name, generator_cls, label):
        file_path = output / f"{base_name}.{ext_name}"
        generator = generator_cls()
        text = generator.generate(builder, direction="LR" if layout=="horizontal" else "TD")
        file_path.write_text(text)
        generated.append(file_path.name)
    
    if format in ['all', 'mermaid']:
        save_text('mmd', MermaidGenerator, 'Mermaid')
        
    if format in ['all', 'bpmn']:
        save_text('bpmn', BpmnGenerator, 'BPMN 2.0')
        
    if format in ['all', 'drawio']:
        save_text('drawio', DrawioGenerator, 'Draw.io')
        
    if format in ['all', 'plantuml', 'puml']:
        save_text('puml', PlantUmlGenerator, 'PlantUML')
        
    if format in ['all', 'svg', 'png', 'pdf']:
        try:
            exporter = GraphvizExporter(builder)
            if format in ['all', 'svg']:
                exporter.export_svg(str(output / base_name))
                generated.append(f"{base_name}.svg")
            if format in ['all', 'png']:
                exporter.export_png(str(output / base_name))
                generated.append(f"{base_name}.png")
            if format in ['all', 'pdf']:
                exporter.export_pdf(str(output / base_name))
                generated.append(f"{base_name}.pdf")
        except ExecutableNotFound:
            console.print("[yellow]Warning: Graphviz executable 'dot' not found. Skipping SVG/PNG/PDF generation. Please install Graphviz.[/yellow]")
            
    for f in generated:
        console.print(f"  - {f}")
        
    console.print("\n[bold green]Success![/bold green]")

if __name__ == "__main__":
    app()
