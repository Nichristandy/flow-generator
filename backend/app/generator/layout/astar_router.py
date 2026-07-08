import heapq
from typing import List, Tuple, Set, Dict
from app.generator.layout.graph import LayoutPoint, BoundingBox

class AStarRouter:
    def __init__(self, canvas_width: int, canvas_height: int, grid_size: int = 20):
        self.grid_size = grid_size
        self.cols = int(canvas_width // grid_size) + 5
        self.rows = int(canvas_height // grid_size) + 5
        self.obstacles: Set[Tuple[int, int]] = set()
        self.edge_paths: Dict[Tuple[int, int], int] = {} # cell -> count of crossings

    def add_obstacle(self, box: BoundingBox, padding: int = 10):
        # Convert box to grid coordinates
        min_x = int((box.x - padding) // self.grid_size)
        max_x = int((box.right + padding) // self.grid_size)
        min_y = int((box.y - padding) // self.grid_size)
        max_y = int((box.bottom + padding) // self.grid_size)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                self.obstacles.add((x, y))

    def mark_path(self, points: List[LayoutPoint]):
        if not points: return
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i+1]
            x1, y1 = int(p1.x // self.grid_size), int(p1.y // self.grid_size)
            x2, y2 = int(p2.x // self.grid_size), int(p2.y // self.grid_size)
            
            if x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self.edge_paths[(x1, y)] = self.edge_paths.get((x1, y), 0) + 1
            elif y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.edge_paths[(x, y1)] = self.edge_paths.get((x, y1), 0) + 1

    def find_path(self, start: LayoutPoint, end: LayoutPoint, source_box: BoundingBox = None, target_box: BoundingBox = None) -> List[LayoutPoint]:
        start_pos = (int(start.x // self.grid_size), int(start.y // self.grid_size))
        end_pos = (int(end.x // self.grid_size), int(end.y // self.grid_size))
        
        # Remove source and target boxes from obstacles temporarily if they overlap with start/end
        temp_removed = set()
        for box in (source_box, target_box):
            if box:
                min_x = int((box.x - 10) // self.grid_size)
                max_x = int((box.right + 10) // self.grid_size)
                min_y = int((box.y - 10) // self.grid_size)
                max_y = int((box.bottom + 10) // self.grid_size)
                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        if (x, y) in self.obstacles:
                            # Only remove if it's strictly close to start or end port
                            if abs(x - start_pos[0]) <= 2 and abs(y - start_pos[1]) <= 2:
                                self.obstacles.remove((x, y))
                                temp_removed.add((x, y))
                            elif abs(x - end_pos[0]) <= 2 and abs(y - end_pos[1]) <= 2:
                                self.obstacles.remove((x, y))
                                temp_removed.add((x, y))

        # A* Search
        open_set = []
        # queue item: (f_score, counter, current_node, current_direction)
        heapq.heappush(open_set, (0, 0, start_pos, None))
        
        came_from = {}
        g_score = {start_pos: 0}
        
        counter = 1
        
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        found = False
        while open_set:
            _, _, current, current_dir = heapq.heappop(open_set)
            
            if current == end_pos:
                found = True
                break
                
            cx, cy = current
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                neighbor = (nx, ny)
                
                # Check bounds
                if not (0 <= nx < self.cols and 0 <= ny < self.rows):
                    continue
                    
                if neighbor in self.obstacles and neighbor != end_pos:
                    continue
                    
                # Calculate cost
                step_cost = 1
                
                # Penalize edge crossings
                if neighbor in self.edge_paths:
                    step_cost += 5 * self.edge_paths[neighbor]
                    
                # Penalize turns heavily to encourage straight orthogonal lines
                new_dir = (dx, dy)
                turn_cost = 0
                if current_dir and current_dir != new_dir:
                    turn_cost = 20
                    
                tentative_g_score = g_score[current] + step_cost + turn_cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = (current, new_dir)
                    g_score[neighbor] = tentative_g_score
                    
                    # h_score: Manhattan distance
                    h_score = abs(end_pos[0] - nx) + abs(end_pos[1] - ny)
                    f_score = tentative_g_score + h_score
                    
                    heapq.heappush(open_set, (f_score, counter, neighbor, new_dir))
                    counter += 1

        # Restore obstacles
        for p in temp_removed:
            self.obstacles.add(p)
            
        if not found:
            return []
            
        # Reconstruct path
        path_cells = []
        curr = end_pos
        while curr in came_from:
            path_cells.append(curr)
            curr = came_from[curr][0]
        path_cells.append(start_pos)
        path_cells.reverse()
        
        # Simplify path to just corner points
        if len(path_cells) < 2:
            return [start, end]
            
        waypoints = [start]
        current_dir = None
        
        for i in range(1, len(path_cells)):
            prev = path_cells[i-1]
            curr = path_cells[i]
            d = (curr[0] - prev[0], curr[1] - prev[1])
            
            if current_dir is None:
                current_dir = d
            elif d != current_dir:
                # Direction changed, previous point is a corner
                px = prev[0] * self.grid_size
                py = prev[1] * self.grid_size
                
                # Ensure it aligns perfectly with start/end if it's on the same axis
                if waypoints and abs(px - waypoints[-1].x) < self.grid_size:
                    px = waypoints[-1].x
                if waypoints and abs(py - waypoints[-1].y) < self.grid_size:
                    py = waypoints[-1].y
                    
                waypoints.append(LayoutPoint(px, py))
                current_dir = d
                
        # Align last segment with end port
        if len(waypoints) > 1:
            last = waypoints[-1]
            if abs(last.x - end.x) < self.grid_size:
                last.x = end.x
            if abs(last.y - end.y) < self.grid_size:
                last.y = end.y
                
        waypoints.append(end)
        
        # Cleanup small micro-segments
        clean_waypoints = [waypoints[0]]
        for i in range(1, len(waypoints) - 1):
            p1 = clean_waypoints[-1]
            p2 = waypoints[i]
            p3 = waypoints[i+1]
            
            # If collinear, skip p2
            if (p1.x == p2.x == p3.x) or (p1.y == p2.y == p3.y):
                continue
            clean_waypoints.append(p2)
        clean_waypoints.append(waypoints[-1])
            
        return clean_waypoints
