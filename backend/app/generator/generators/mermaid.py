from generators.base import BaseGenerator
from graph.builder import GraphBuilder

class MermaidGenerator(BaseGenerator):
    def generate(self, builder: GraphBuilder, **kwargs) -> str:
        direction = kwargs.get("direction", "LR")
        lines = [f"graph {direction}"]
        
        # Group nodes by lane to use subgraphs
        nodes_by_lane = {}
        for node_id, node in builder.nodes.items():
            if node.lane:
                if node.lane not in nodes_by_lane:
                    nodes_by_lane[node.lane] = []
                nodes_by_lane[node.lane].append(node)
                
        def format_node(n):
            name = n.label or n.type
            name = name.replace('"', '\\"') # escape quotes
            if n.type in ("exclusive_gateway", "parallel_gateway"):
                return f'{n.id}{{{{"{name}"}}}}'
            elif n.type in ("start", "end"):
                return f'{n.id}(("{name}"))'
            else:
                return f'{n.id}["{name}"]'
                
        lane_idx = 0
        for lane_name, nodes in nodes_by_lane.items():
            if not nodes:
                continue
            lane_id = f"lane_{lane_idx}"
            lane_idx += 1
            lines.append(f"    subgraph {lane_id} [{lane_name}]")
            for node in nodes:
                lines.append(f"        {format_node(node)}")
            lines.append("    end")
            
        for source, target, edge_data in builder.graph.edges(data=True):
            label = f"|{edge_data['label']}|" if edge_data.get("label") else ""
            lines.append(f"    {source} -->{label} {target}")
            
        return "\n".join(lines)
