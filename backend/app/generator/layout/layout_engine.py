from typing import Dict, List
from app.generator.graph.builder import GraphBuilder
from app.generator.layout.graph import LayoutNode, LayoutEdge
from app.generator.layout.node_placer import NodePlacer
from app.generator.layout.edge_router import EdgeRouter
from app.generator.layout.obstacle_detector import ObstacleDetector

class LayoutEngine:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.nodes: Dict[str, LayoutNode] = {}
        self.edges: List[LayoutEdge] = []
        
    def execute(self):
        # 1. Place nodes
        placer = NodePlacer(self.builder)
        self.nodes = placer.place_nodes()
        
        # 2. Register obstacles
        detector = ObstacleDetector()
        for node in self.nodes.values():
            detector.add_obstacle(node.box)
            
        # 3. Route edges
        router = EdgeRouter(self.builder, self.nodes, detector)
        self.edges = router.route_edges()
        
        # 4. Sync coordinates to original graph structure for exporters
        for node_id, lnode in self.nodes.items():
            b_node = self.builder.nodes[node_id]
            b_node.x = lnode.box.x
            b_node.y = lnode.box.y
            b_node.metadata["width"] = lnode.box.width
            b_node.metadata["height"] = lnode.box.height
            b_node.col = lnode.col
            b_node.row = lnode.row
            
            if b_node.lane in self.builder.graph.graph.get("lanes", {}):
                lane_data = self.builder.graph.graph["lanes"][b_node.lane]
                b_node.metadata["relative_x"] = b_node.x - lane_data["x"]
                b_node.metadata["relative_y"] = b_node.y - lane_data["y"]
                
        for edge in self.edges:
            # Update edge data with waypoints
            edge_data = self.builder.graph.edges[edge.source_id, edge.target_id]
            waypoints_tuple = [(pt.x, pt.y) for pt in edge.waypoints]
            edge_data["waypoints"] = waypoints_tuple
            edge_data["drawio_waypoints"] = waypoints_tuple
