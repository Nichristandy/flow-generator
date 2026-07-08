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
compiler = AstCompiler(ast)
builder = compiler.compile()

engine = LayoutEngine(builder)
engine.execute()

for n_id, n in engine.nodes.items():
    print(f"{n.label}: col={n.col}, row={n.row}")
