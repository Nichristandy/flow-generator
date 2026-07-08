import asyncio
from app.generator.parser.flow_parser import FlowParser
from app.generator.graph.compiler import AstCompiler
from app.generator.layout.layout_engine import LayoutEngine
from app.generator.layout.preview_renderer import PreviewRenderer

dsl = """
Start
Procurement: Create Purchase Order
LABEL PO Loop
Approval Director: Review PO
IF PO is approved
    Receipt Warehouse: Receive Goods
ELSE
    Procurement: Revise PO
    GOTO PO Loop
ENDIF
End
"""

parser = FlowParser()
ast = parser.parse(dsl)
compiler = AstCompiler(ast)
builder = compiler.compile()

engine = LayoutEngine(builder)
engine.execute()

renderer = PreviewRenderer(builder, engine.nodes, engine.edges)
svg = renderer.render_svg()
lines = svg.split('\n')
for line in lines:
    if '<path' in line:
        print(line)
