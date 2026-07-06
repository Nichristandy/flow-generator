from app.generator.parser.ast import FlowAst, AstStart, AstEnd, AstIf, AstElse, AstEndIf

class ValidationError(Exception):
    pass

class AstValidator:
    def __init__(self, ast: FlowAst):
        self.ast = ast

    def validate(self):
        self._check_start_end_events()
        self._check_balanced_branches()
        
    def _check_start_end_events(self):
        has_start = any(isinstance(n, AstStart) for n in self.ast.nodes)
        has_end = any(isinstance(n, AstEnd) for n in self.ast.nodes)
        
        if not has_start:
            raise ValidationError("Missing Start node.")
        if not has_end:
            raise ValidationError("Missing End node.")
            
    def _check_balanced_branches(self):
        stack = []
        
        for idx, node in enumerate(self.ast.nodes):
            if isinstance(node, AstIf):
                stack.append("IF")
            elif isinstance(node, AstElse):
                if not stack or stack[-1] != "IF":
                    raise ValidationError("ELSE without a matching IF.")
                # We can mark it as ELSE to ensure no double ELSE
                stack[-1] = "ELSE"
            elif isinstance(node, AstEndIf):
                if not stack:
                    raise ValidationError("ENDIF without a matching IF/ELSE.")
                stack.pop()
                
        if stack:
            raise ValidationError("Unclosed IF branch (missing ENDIF).")
