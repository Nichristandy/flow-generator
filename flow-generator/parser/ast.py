from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AstNode:
    pass

@dataclass
class AstStart(AstNode):
    pass

@dataclass
class AstEnd(AstNode):
    pass

@dataclass
class AstTask(AstNode):
    actor: str
    name: str

@dataclass
class AstIf(AstNode):
    condition: str

@dataclass
class AstElse(AstNode):
    pass

@dataclass
class AstEndIf(AstNode):
    pass

@dataclass
class AstGoto(AstNode):
    target: str

@dataclass
class FlowAst:
    nodes: List[AstNode]
