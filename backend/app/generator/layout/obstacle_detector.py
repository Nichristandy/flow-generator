from typing import List
from app.generator.layout.graph import BoundingBox, LayoutPoint

class ObstacleDetector:
    def __init__(self, margin: float = 10.0):
        self.obstacles: List[BoundingBox] = []
        self.margin = margin

    def add_obstacle(self, box: BoundingBox):
        self.obstacles.append(box)

    def is_point_free(self, pt: LayoutPoint) -> bool:
        for obs in self.obstacles:
            if obs.contains_point(pt, margin=self.margin):
                return False
        return True

    def is_segment_free(self, p1: LayoutPoint, p2: LayoutPoint) -> bool:
        # Assume orthogonal segments
        min_x = min(p1.x, p2.x)
        max_x = max(p1.x, p2.x)
        min_y = min(p1.y, p2.y)
        max_y = max(p1.y, p2.y)

        for obs in self.obstacles:
            if p1.y == p2.y:
                # Horizontal segment
                if (obs.top - self.margin < p1.y < obs.bottom + self.margin):
                    if not (max_x < obs.left - self.margin or min_x > obs.right + self.margin):
                        return False
            else:
                # Vertical segment
                if (obs.left - self.margin < p1.x < obs.right + self.margin):
                    if not (max_y < obs.top - self.margin or min_y > obs.bottom + self.margin):
                        return False
        return True
