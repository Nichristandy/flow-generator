import asyncio
from app.generator.parser.flow_parser import FlowParser
from app.generator.graph.compiler import AstCompiler
from app.generator.layout.layout_engine import LayoutEngine

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

print("Nodes in Graph:")
for n_id, n in builder.nodes.items():
    print(n.actor, n.name if hasattr(n, 'name') else n.label)

engine = LayoutEngine(builder)
engine.execute()

for u, v, d in builder.graph.edges(data=True):
    print(f"Edge {builder.nodes[u].label} -> {builder.nodes[v].label} waypoints: {len(d.get('waypoints', []))}")
