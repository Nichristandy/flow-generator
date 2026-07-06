from abc import ABC, abstractmethod
from parser.ast import FlowAst

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> FlowAst:
        """Parses the input string and returns a FlowAst."""
        pass
