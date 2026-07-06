import networkx as nx
from typing import Dict, List, Tuple
from graph.builder import GraphBuilder, Node

class LayoutOptimizer:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.graph = builder.get_graph()
        self.grid_size_x = 250
        self.grid_size_y = 150
        self.start_x = 100
        self.start_y = 100

    def optimize(self):
        # 1. Topological levelizer (Depth assignment)
        self._assign_levels()
        
        # 2. Swimlane Y offsets assignment
        lane_y_offsets = self._assign_lanes()
        
        # 3. Crossing reduction heuristics & Node coordinates
        self._assign_coordinates(lane_y_offsets)
        
        # 4. Route edges to avoid overlaps
        self._route_edges()

    def _route_edges(self):
        for u, v, data in self.graph.edges(data=True):
            node_u = self.builder.nodes[u]
            node_v = self.builder.nodes[v]
            
            extra_style = []
            waypoints = []
            
            # If backward edge (e.g. No branch returning to a previous step)
            if getattr(node_v, 'col', 0) < getattr(node_u, 'col', 0):
                # Exit top of u, enter top of v
                extra_style.append("exitX=0.5;exitY=0;exitDx=0;exitDy=0")
                extra_style.append("entryX=0.5;entryY=0;entryDx=0;entryDy=0")
                
                # Find the lane y-coordinate (lane bounding box top)
                lane_u_y = self.builder.graph.graph["lanes"][node_u.lane]["y"]
                lane_v_y = self.builder.graph.graph["lanes"][node_v.lane]["y"]
                
                # We want to go higher than the highest of the two lanes to avoid crossing
                min_y = min(lane_u_y, lane_v_y)
                
                # Offset y so it goes above the lane title and nodes
                route_y = min_y - 20
                
                # The x coordinates should be centered on the nodes
                x_u = node_u.x + node_u.metadata.get("width", 120) / 2
                x_v = node_v.x + node_v.metadata.get("width", 120) / 2
                
                # Add waypoints
                waypoints.append((x_u, route_y))
                waypoints.append((x_v, route_y))
                
            else:
                # Forward edge cross-lane routing logic
                if node_u.lane != node_v.lane:
                    lane_u_y = self.builder.graph.graph["lanes"][node_u.lane]["y"]
                    lane_v_y = self.builder.graph.graph["lanes"][node_v.lane]["y"]
                    
                    if lane_v_y > lane_u_y:
                        # v is below u, exit bottom of u, enter top of v
                        extra_style.append("exitX=0.5;exitY=1;exitDx=0;exitDy=0")
                        extra_style.append("entryX=0.5;entryY=0;entryDx=0;entryDy=0")
                    else:
                        # v is above u, exit top of u, enter bottom of v
                        extra_style.append("exitX=0.5;exitY=0;exitDx=0;exitDy=0")
                        extra_style.append("entryX=0.5;entryY=1;entryDx=0;entryDy=0")
                else:
                    pass # Same lane: drawio default orthogonal (right to left) handles it best
                    
            if extra_style:
                data['extra_style'] = ";".join(extra_style) + ";"
            if waypoints:
                data['drawio_waypoints'] = waypoints
                # Also set regular waypoints for BPMN, but let connector update them if it wants
                data['waypoints'] = [
                    (node_u.x + node_u.metadata.get("width", 120) / 2, node_u.y), # start
                    waypoints[0],
                    waypoints[1],
                    (node_v.x + node_v.metadata.get("width", 120) / 2, node_v.y)  # end
                ]

    def _assign_levels(self):
        # Longest path from start nodes to each node in DAG
        start_nodes = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        
        # Initialize all levels to 0
        for node_id in self.graph.nodes:
            self.builder.nodes[node_id].level = 0
            
        # Standard DAG longest path for level assignment
        if nx.is_directed_acyclic_graph(self.graph):
            for node_id in nx.topological_sort(self.graph):
                node_level = self.builder.nodes[node_id].level
                for successor in self.graph.successors(node_id):
                    if self.builder.nodes[successor].level <= node_level:
                        self.builder.nodes[successor].level = node_level + 1
        else:
            # Fallback for cycles (BFS layer assignment)
            visited = set(start_nodes)
            queue = [(n, 0) for n in start_nodes]
            while queue:
                curr, depth = queue.pop(0)
                self.builder.nodes[curr].level = max(self.builder.nodes[curr].level, depth)
                for neighbor in self.graph.successors(curr):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1))

    def _assign_lanes(self) -> Dict[str, float]:
        lanes = []
        for node in self.builder.nodes.values():
            if node.lane and node.lane not in lanes:
                lanes.append(node.lane)
                
        lane_y_offsets = {}
        current_y = self.start_y
        
        for lane in lanes:
            lane_y_offsets[lane] = current_y
            # We'll store lane info globally in the builder metadata for the generators to use
            if "lanes" not in self.builder.graph.graph:
                self.builder.graph.graph["lanes"] = {}
                
            self.builder.graph.graph["lanes"][lane] = {
                "y": current_y,
                "height": self.grid_size_y,
                "x": self.start_x - 50,
                "width": 1000 # Default width, updated later
            }
            current_y += self.grid_size_y
            
        return lane_y_offsets

    def _assign_coordinates(self, lane_y_offsets: Dict[str, float]):
        # Width and height initialization
        for node_id in self.graph.nodes:
            node = self.builder.nodes[node_id]
            if node.type in ("start", "end"):
                node.metadata["width"] = 40
                node.metadata["height"] = 40
            elif node.type in ("exclusive_gateway", "parallel_gateway"):
                node.metadata["width"] = 60
                node.metadata["height"] = 60
            else:
                node.metadata["width"] = 120
                node.metadata["height"] = 60
                
        # Grid Compaction Layout
        occupied = set() # (lane, col)
        
        sorted_nodes = list(nx.topological_sort(self.graph)) if nx.is_directed_acyclic_graph(self.graph) else self.graph.nodes
        
        for node_id in sorted_nodes:
            node = self.builder.nodes[node_id]
            
            min_col = 0
            for parent_id in self.graph.predecessors(node_id):
                parent_node = self.builder.nodes[parent_id]
                parent_col = getattr(parent_node, 'col', 0)
                
                # If same lane, we MUST advance column.
                # If different lane, we can try to vertically stack (same column)
                if parent_node.lane == node.lane:
                    min_col = max(min_col, parent_col + 1)
                else:
                    min_col = max(min_col, parent_col)
                    
            # Find first available column
            col = min_col
            while (node.lane, col) in occupied:
                col += 1
                
            node.col = col
            occupied.add((node.lane, col))
            
        max_x = 0
        
        for node_id in self.graph.nodes:
            node = self.builder.nodes[node_id]
            col = getattr(node, 'col', 0)
            
            # X coordinate based on grid column
            x = self.start_x + (col * self.grid_size_x)
            
            # Center small nodes (like start/end/gateways) in the 120px wide grid cell
            if node.metadata["width"] < 120:
                x += (120 - node.metadata["width"]) / 2
                
            max_x = max(max_x, x)
            node.x = x
            
            # Y coordinate based on lane
            if node.lane in lane_y_offsets:
                lane_y = lane_y_offsets[node.lane]
                # Center vertically in the lane
                node.y = lane_y + (self.grid_size_y / 2) - (node.metadata["height"] / 2)
            else:
                node.y = self.start_y
                
            # For Drawio/BPMN, we need relative coordinates if it's in a lane
            if node.lane in self.builder.graph.graph.get("lanes", {}):
                lane_data = self.builder.graph.graph["lanes"][node.lane]
                node.metadata["relative_x"] = node.x - lane_data["x"]
                node.metadata["relative_y"] = node.y - lane_data["y"]
                
        # Update lane widths based on max_x
        if "lanes" in self.builder.graph.graph:
            for lane, data in self.builder.graph.graph["lanes"].items():
                data["width"] = max_x + self.grid_size_x - data["x"]
