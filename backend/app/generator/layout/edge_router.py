from typing import List, Dict
from app.generator.graph.builder import GraphBuilder
from app.generator.layout.graph import LayoutNode, LayoutEdge, LayoutPoint, PortDirection
from app.generator.layout.obstacle_detector import ObstacleDetector
from app.generator.layout.astar_router import AStarRouter

class EdgeRouter:
    def __init__(self, builder: GraphBuilder, layout_nodes: Dict[str, LayoutNode], detector: ObstacleDetector):
        self.builder = builder
        self.graph = builder.get_graph()
        self.layout_nodes = layout_nodes
        self.detector = detector
        
    def route_edges(self) -> List[LayoutEdge]:
        edges = []
        
        # Determine canvas size for AStar
        max_x = max([n.box.right for n in self.layout_nodes.values()] + [1500]) + 200
        max_y = max([n.box.bottom for n in self.layout_nodes.values()] + [1500]) + 200
        
        router = AStarRouter(max_x, max_y, grid_size=20)
        
        # Mark all node boxes as obstacles
        for node in self.layout_nodes.values():
            router.add_obstacle(node.box, padding=10)
            
        for u, v, data in self.graph.edges(data=True):
            source_node = self.layout_nodes[u]
            target_node = self.layout_nodes[v]
            
            # 1. Forward flow
            if source_node.col < target_node.col:
                if source_node.type in ("exclusive_gateway", "parallel_gateway"):
                    if target_node.box.y > source_node.box.y + 30:
                        start = source_node.get_port(PortDirection.SOUTH)
                    elif target_node.box.y < source_node.box.y - 30:
                        start = source_node.get_port(PortDirection.NORTH)
                    else:
                        start = source_node.get_port(PortDirection.EAST)
                else:
                    start = source_node.get_port(PortDirection.EAST)
                
                end = target_node.get_port(PortDirection.WEST)
                
            # 2. Backward flow (e.g. Return loops)
            elif source_node.col > target_node.col:
                start = source_node.get_port(PortDirection.WEST)
                end = target_node.get_port(PortDirection.NORTH)
                # Ensure end port is NORTH to avoid looping around the front
                
            # 3. Vertical flow (Same column stacking)
            else:
                if source_node.box.top < target_node.box.top:
                    # Going DOWN
                    start = source_node.get_port(PortDirection.SOUTH)
                    end = target_node.get_port(PortDirection.NORTH)
                else:
                    # Going UP in same column
                    start = source_node.get_port(PortDirection.NORTH)
                    end = target_node.get_port(PortDirection.SOUTH)
                    
            # Find path with A*
            waypoints = router.find_path(start, end, source_node.box, target_node.box)
            
            # If A* fails, fallback to simple Manhattan
            if not waypoints:
                mid_x = start.x + (end.x - start.x) / 2
                waypoints = [
                    start,
                    LayoutPoint(mid_x, start.y),
                    LayoutPoint(mid_x, end.y),
                    end
                ]
                
            router.mark_path(waypoints)
                    
            edges.append(LayoutEdge(
                source_id=u,
                target_id=v,
                label=data.get("label", ""),
                waypoints=waypoints
            ))
            
        return edges
