import graphviz
from app.generator.graph.builder import GraphBuilder

class GraphvizExporter:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.graph = builder.graph
        
    def _build_graph(self) -> graphviz.Digraph:
        dot = graphviz.Digraph(comment="Generated Process")
        dot.attr(rankdir='LR')
        
        # Lanes as subgraphs
        nodes_by_lane = {}
        for node_id, node in self.builder.nodes.items():
            if node.lane:
                if node.lane not in nodes_by_lane:
                    nodes_by_lane[node.lane] = []
                nodes_by_lane[node.lane].append(node)
                
        def format_shape(n):
            if n.type in ['start', 'end']: return 'circle'
            if n.type in ['exclusive_gateway', 'parallel_gateway']: return 'diamond'
            return 'box'
            
        lane_idx = 0
        for lane_name, nodes in nodes_by_lane.items():
            if not nodes: continue
            lane_id = f"lane_{lane_idx}"
            lane_idx += 1
            with dot.subgraph(name=f'cluster_{lane_id}') as c:
                c.attr(label=lane_name)
                for node in nodes:
                    c.node(node.id, node.label or node.type, shape=format_shape(node))
                    
        for source, target, edge_data in self.graph.edges(data=True):
            dot.edge(source, target, label=edge_data.get('label', ""))
            
        return dot

    def export_svg(self, path: str):
        dot = self._build_graph()
        dot.render(outfile=f"{path}.svg", format='svg', cleanup=True)
        
    def export_png(self, path: str):
        dot = self._build_graph()
        dot.render(outfile=f"{path}.png", format='png', cleanup=True)
        
    def export_pdf(self, path: str):
        dot = self._build_graph()
        dot.render(outfile=f"{path}.pdf", format='pdf', cleanup=True)
