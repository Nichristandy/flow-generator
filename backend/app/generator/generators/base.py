from abc import ABC, abstractmethod
from graph.builder import GraphBuilder

class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, builder: GraphBuilder, **kwargs) -> str:
        """Generates the diagram representation from a GraphBuilder."""
        pass
