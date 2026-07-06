from typing import List, Dict
from app.generator.graph.builder import GraphBuilder
from app.generator.layout.graph import LayoutNode, LayoutEdge, LayoutPoint, PortDirection
from app.generator.layout.obstacle_detector import ObstacleDetector

class EdgeRouter:
    def __init__(self, builder: GraphBuilder, layout_nodes: Dict[str, LayoutNode], detector: ObstacleDetector):
        self.builder = builder
        self.graph = builder.get_graph()
        self.layout_nodes = layout_nodes
        self.detector = detector
        
    def route_edges(self) -> List[LayoutEdge]:
        edges = []
        for u, v, data in self.graph.edges(data=True):
            source_node = self.layout_nodes[u]
            target_node = self.layout_nodes[v]
            
            # 1. Forward flow
            if source_node.col < target_node.col:
                # Default Forward: East -> West
                start = source_node.get_port(PortDirection.EAST)
                
                # If target is slightly offset vertically, enter West, else enter West.
                end = target_node.get_port(PortDirection.WEST)
                
                mid_x = start.x + (end.x - start.x) / 2
                waypoints = [
                    start,
                    LayoutPoint(mid_x, start.y),
                    LayoutPoint(mid_x, end.y),
                    end
                ]
                
            # 2. Backward flow (e.g. Return loops)
            elif source_node.col > target_node.col:
                start = source_node.get_port(PortDirection.SOUTH)
                end = target_node.get_port(PortDirection.NORTH)
                
                # Route around the outside (bottom of lane)
                # Find the lowest point in the involved lanes
                route_y = max(source_node.box.bottom, target_node.box.bottom) + 60
                
                waypoints = [
                    start,
                    LayoutPoint(start.x, route_y),
                    LayoutPoint(end.x, route_y),
                    end
                ]
                
            # 3. Vertical flow (Same column stacking)
            else:
                if source_node.box.top < target_node.box.top:
                    # Going DOWN
                    start = source_node.get_port(PortDirection.SOUTH)
                    end = target_node.get_port(PortDirection.NORTH)
                    
                    mid_y = start.y + (end.y - start.y) / 2
                    waypoints = [
                        start,
                        LayoutPoint(start.x, mid_y),
                        LayoutPoint(end.x, mid_y),
                        end
                    ]
                else:
                    # Going UP in same column
                    start = source_node.get_port(PortDirection.NORTH)
                    end = target_node.get_port(PortDirection.SOUTH)
                    
                    mid_y = start.y + (end.y - start.y) / 2
                    waypoints = [
                        start,
                        LayoutPoint(start.x, mid_y),
                        LayoutPoint(end.x, mid_y),
                        end
                    ]
                    
            edges.append(LayoutEdge(
                source_id=u,
                target_id=v,
                label=data.get("label", ""),
                waypoints=waypoints
            ))
            
        return edges
