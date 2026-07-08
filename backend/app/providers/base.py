from abc import ABC, abstractmethod
from typing import Optional, List, Dict

class AIProvider(ABC):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key
        self.model = model
        
    @abstractmethod
    async def generate_dsl(self, conversation: List[Dict[str, str]], mode: str = "dsl") -> str:
        """Generate DSL (or JSON) from a conversation history."""
        pass
    
    @abstractmethod
    async def improve_dsl(self, current_dsl: str, instructions: Optional[str], mode: str = "dsl") -> str:
        """Improve an existing flow based on instructions."""
        pass
        
    @abstractmethod
    async def repair_dsl(self, dsl: str, error_message: str, mode: str = "dsl") -> str:
        """Repair a failing DSL/JSON."""
        pass
