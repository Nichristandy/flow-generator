import networkx as nx
from typing import Dict, List, Set, Tuple
from app.generator.graph.builder import GraphBuilder, Node
from app.generator.layout.graph import LayoutNode, BoundingBox

class NodePlacer:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.graph = builder.get_graph()
        self.grid_size_x = 220
        self.grid_size_y = 120
        self.start_x = 100
        self.start_y = 100
        self.lane_y_offsets: Dict[str, float] = {}

    def place_nodes(self) -> Dict[str, LayoutNode]:
        layout_nodes: Dict[str, LayoutNode] = {}
        
        for node_id in self.graph.nodes:
            node = self.builder.nodes[node_id]
            layout_node = LayoutNode(id=node.id, type=node.type, lane=node.lane, label=node.label)
            if node.type in ("start", "end"):
                width, height = 40, 40
            elif node.type in ("exclusive_gateway", "parallel_gateway"):
                width, height = 80, 80
            else:
                width, height = 140, 60
            layout_node.box = BoundingBox(0, 0, width, height)
            layout_nodes[node.id] = layout_node

        lanes = []
        for node in layout_nodes.values():
            if node.lane and node.lane not in lanes:
                lanes.append(node.lane)

        occupied: Set[Tuple[str, int, int]] = set()
        
        try:
            sorted_nodes = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            sorted_nodes = list(self.graph.nodes)

        node_grid_pos = {}

        for node_id in sorted_nodes:
            node = layout_nodes[node_id]
            preds = list(self.graph.predecessors(node_id))
            
            if not preds:
                col, row = 0, 0
            else:
                max_parent_col = 0
                for p in preds:
                    if p in node_grid_pos:
                        max_parent_col = max(max_parent_col, node_grid_pos[p][0])
                
                parent_id = preds[0]
                parent_node = layout_nodes.get(parent_id)
                
                col = max_parent_col
                
                # Rule 20 & 21: Allow vertical stacking (same column) if single parent and parent has single child, regardless of lane changes
                if parent_node and len(preds) == 1 and self.graph.out_degree(parent_id) == 1:
                    pass
                else:
                    col += 1
                
                row = 0
                
            while (node.lane, col, row) in occupied:
                row += 1
            
            node_grid_pos[node_id] = (col, row)
            node.col = col
            node.row = row
            occupied.add((node.lane, col, row))

        lane_rows = {lane: 0 for lane in lanes}
        for (lane, col, row) in occupied:
            lane_rows[lane] = max(lane_rows[lane], row + 1)
            
        current_y = self.start_y
        if "lanes" not in self.builder.graph.graph:
            self.builder.graph.graph["lanes"] = {}
            
        for lane in lanes:
            self.lane_y_offsets[lane] = current_y
            rows = max(1, lane_rows[lane])
            lane_height = max(200, rows * self.grid_size_y + 60)
            
            self.builder.graph.graph["lanes"][lane] = {
                "y": current_y,
                "height": lane_height,
                "x": self.start_x - 50,
                "width": 1000 
            }
            current_y += lane_height
            
        max_x = 0
        for node_id, node in layout_nodes.items():
            col, row = node.col, node.row
            
            x = self.start_x + (col * self.grid_size_x)
            if node.box.width < 140:
                x += (140 - node.box.width) / 2
                
            y = self.lane_y_offsets.get(node.lane, self.start_y) + (row * self.grid_size_y) + 40
            
            node.box.x = x
            node.box.y = y
            
            max_x = max(max_x, x + node.box.width)
            
        for lane in lanes:
            self.builder.graph.graph["lanes"][lane]["width"] = max(1000, max_x + self.grid_size_x - self.start_x + 50)
            
        return layout_nodes
