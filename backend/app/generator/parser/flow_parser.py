import re
from parser.base import BaseParser
from parser.ast import FlowAst, AstStart, AstEnd, AstTask, AstIf, AstElse, AstEndIf, AstGoto

class FlowParser(BaseParser):
    """Parses simple DSL or Markdown line-by-line flow into a FlowAst."""
    
    def parse(self, content: str) -> FlowAst:
        ast = FlowAst(nodes=[])
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        for line in lines:
            upper_line = line.upper()
            
            if upper_line in ("START", "START EVENT"):
                ast.nodes.append(AstStart())
                continue
                
            if upper_line in ("END", "END EVENT"):
                ast.nodes.append(AstEnd())
                continue
                
            if upper_line.startswith("IF "):
                condition = line[3:].strip()
                ast.nodes.append(AstIf(condition=condition))
                continue
                
            if upper_line.startswith("GOTO "):
                target = line[5:].strip()
                ast.nodes.append(AstGoto(target=target))
                continue
                
            if upper_line == "ELSE":
                ast.nodes.append(AstElse())
                continue
                
            if upper_line == "ENDIF":
                ast.nodes.append(AstEndIf())
                continue
                
            # Task logic
            match = re.match(r"^([^:]+):\s*(.+)$", line)
            if match:
                lane_name = match.group(1).strip()
                task_name = match.group(2).strip()
                ast.nodes.append(AstTask(actor=lane_name, name=task_name))
                continue
                
            match_by = re.match(r"^(.+)\s+by\s+(.+)$", line)
            if match_by:
                task_name = match_by.group(1).strip()
                lane_name = match_by.group(2).strip()
                ast.nodes.append(AstTask(actor=lane_name, name=task_name))
                continue
                
            # Default task without lane
            ast.nodes.append(AstTask(actor="System", name=line))
                
        return ast
