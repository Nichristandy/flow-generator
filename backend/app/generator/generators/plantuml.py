from app.generator.generators.base import BaseGenerator
from app.generator.graph.builder import GraphBuilder

class PlantUmlGenerator(BaseGenerator):
    def generate(self, builder: GraphBuilder, **kwargs) -> str:
        lines = ["@startuml"]
        
        # Group nodes by lane
        nodes_by_lane = {}
        for node_id, node in builder.nodes.items():
            if node.lane:
                if node.lane not in nodes_by_lane:
                    nodes_by_lane[node.lane] = []
                nodes_by_lane[node.lane].append(node)
                
        def get_puml_id(n):
            if n.type == "start": return "start"
            if n.type == "end": return "stop"
            return f"n_{n.id}"
            
        def define_node(n):
            if n.type in ("start", "end"):
                return ""
            if n.type in ("exclusive_gateway", "parallel_gateway"):
                return f"diamond {get_puml_id(n)}"
            return f"usecase {get_puml_id(n)} as \"{n.label}\""
            
        for lane_name, nodes in nodes_by_lane.items():
            if not nodes: continue
            lines.append(f"package \"{lane_name}\" {{")
            for node in nodes:
                node_def = define_node(node)
                if node_def: lines.append("    " + node_def)
            lines.append("}")
            
        for source, target, edge_data in builder.graph.edges(data=True):
            source_id = get_puml_id(builder.nodes[source])
            target_id = get_puml_id(builder.nodes[target])
            label = f" : {edge_data['label']}" if edge_data.get("label") else ""
            lines.append(f"{source_id} --> {target_id}{label}")
            
        lines.append("@enduml")
        return "\n".join(lines)
