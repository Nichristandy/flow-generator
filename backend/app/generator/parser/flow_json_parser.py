import json
from typing import List, Dict, Any
from app.generator.parser.ast import FlowAst, AstStart, AstEnd, AstTask, AstIf, AstElse, AstEndIf, AstGoto, AstLabel

class FlowJsonParser:
    def parse(self, json_str: str) -> FlowAst:
        """Parses a JSON array into a FlowAst."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

        if not isinstance(data, list):
            raise ValueError("Flow JSON must be a list of blocks")

        nodes = []
        for block in data:
            b_type = block.get("type", "").lower()
            if b_type == "start":
                nodes.append(AstStart())
            elif b_type == "end":
                nodes.append(AstEnd())
            elif b_type == "task":
                nodes.append(AstTask(actor=block.get("actor", "System"), name=block.get("action", "Task")))
            elif b_type == "if":
                nodes.append(AstIf(condition=block.get("condition", "Condition")))
            elif b_type == "else":
                nodes.append(AstElse())
            elif b_type == "endif":
                nodes.append(AstEndIf())
            elif b_type == "goto":
                nodes.append(AstGoto(target=block.get("target", "")))
            elif b_type == "label":
                nodes.append(AstLabel(name=block.get("name", "")))

        # Ensure Start and End exist
        if not any(isinstance(n, AstStart) for n in nodes):
            nodes.insert(0, AstStart())
        if not any(isinstance(n, AstEnd) for n in nodes):
            nodes.append(AstEnd())

        return FlowAst(nodes=nodes)
