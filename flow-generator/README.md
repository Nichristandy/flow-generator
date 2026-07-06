# AI Flow Generator

A modular Python application that converts simple business process descriptions into multiple diagram formats automatically.

## Supported Formats

- Mermaid (Flowchart & Swimlanes)
- BPMN 2.0 XML
- Draw.io XML
- PlantUML
- SVG, PNG, PDF (via Graphviz)

## Setup

```bash
# Set up a virtual environment and install dependencies
pip install typer rich pydantic lxml jinja2 pyyaml graphviz cairosvg pillow xmltodict
```

*Note: Ensure you have Graphviz installed on your system if you want to generate SVG, PNG, or PDF formats (`brew install graphviz` or `sudo apt install graphviz`).*

## Usage

```bash
python cli.py examples/procurement.md --format all
```

Options:
- `--format`: `mermaid`, `bpmn`, `drawio`, `plantuml`, `svg`, `png`, `pdf`, or `all`.
- `--layout`: `horizontal` or `vertical`.
- `--output`: Output directory.

## Architecture

1. **Parser**: Converts YAML, Markdown, or Custom DSL into an internal `Process` model.
2. **Validator**: Checks for process integrity (e.g., missing start events, disconnected nodes).
3. **Layout Engine**: Computes X/Y coordinates for BPMN and Draw.io compatibility.
4. **Generators/Exporters**: Render the internal model into final formats.
