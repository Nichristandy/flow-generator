import yaml
from app.generator.parser.base import BaseParser
from app.generator.parser.ast import FlowAst, AstTask, AstStart, AstEnd, AstIf, AstElse, AstEndIf

class YamlParser(BaseParser):
    def parse(self, content: str) -> FlowAst:
        # Not fully implemented for new AST architecture
        raise NotImplementedError("YAML parser is not yet implemented for the new architecture.")
