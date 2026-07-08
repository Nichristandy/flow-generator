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
    Finance: Process Vendor Bill
    Finance: Make Vendor Payment
ELSE
    Procurement: Revise PO
    GOTO PO Loop
ENDIF
End
"""

parser = FlowParser()
ast = parser.parse(dsl)
for node in ast.nodes:
    print(node)

compiler = AstCompiler(ast)
builder = compiler.compile()

print("\nNodes in Graph:")
for n_id, n in builder.nodes.items():
    print(n.actor, n.name if hasattr(n, 'name') else n.label)

print("\nEdges:")
for u, v, d in builder.graph.edges(data=True):
    u_n = builder.nodes[u]
    v_n = builder.nodes[v]
    print(f"{u_n.label} -> {v_n.label} ({d})")

try:
    engine = LayoutEngine(builder)
    engine.execute()
    print("\nLayout Engine executed successfully")
    for u, v, d in builder.graph.edges(data=True):
        print(f"Edge {u} -> {v} waypoints: {len(d.get('waypoints', []))}")
except Exception as e:
    print(f"\nLayout Engine failed: {e}")
