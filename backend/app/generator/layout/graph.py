from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum

class PortDirection(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

@dataclass
class LayoutPoint:
    x: float
    y: float

@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    @property
    def top(self) -> float: return self.y
    @property
    def bottom(self) -> float: return self.y + self.height
    @property
    def left(self) -> float: return self.x
    @property
    def right(self) -> float: return self.x + self.width

    def intersects(self, other: 'BoundingBox', margin: float = 0) -> bool:
        return not (self.right + margin <= other.left or
                    self.left - margin >= other.right or
                    self.bottom + margin <= other.top or
                    self.top - margin >= other.bottom)
    
    def contains_point(self, pt: LayoutPoint, margin: float = 0) -> bool:
        return (self.left - margin < pt.x < self.right + margin) and \
               (self.top - margin < pt.y < self.bottom + margin)

@dataclass
class LayoutNode:
    id: str
    type: str # 'start', 'end', 'task', 'exclusive_gateway', 'parallel_gateway'
    lane: str
    label: str
    box: BoundingBox = field(default_factory=lambda: BoundingBox(0, 0, 0, 0))
    # Logical grid positions
    col: int = 0
    row: int = 0
    
    def get_port(self, direction: PortDirection) -> LayoutPoint:
        if direction == PortDirection.NORTH:
            return LayoutPoint(self.box.x + self.box.width / 2, self.box.top)
        elif direction == PortDirection.SOUTH:
            return LayoutPoint(self.box.x + self.box.width / 2, self.box.bottom)
        elif direction == PortDirection.EAST:
            return LayoutPoint(self.box.right, self.box.y + self.box.height / 2)
        elif direction == PortDirection.WEST:
            return LayoutPoint(self.box.left, self.box.y + self.box.height / 2)
        return LayoutPoint(self.box.x, self.box.y)

@dataclass
class LayoutEdge:
    source_id: str
    target_id: str
    label: str = ""
    waypoints: List[LayoutPoint] = field(default_factory=list)
