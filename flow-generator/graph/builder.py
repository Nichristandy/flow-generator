import networkx as nx
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class Node:
    id: str
    label: str
    actor: str
    lane: str
    type: str  # 'start', 'end', 'task', 'exclusive_gateway', 'parallel_gateway'
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    level: int = 0
    x: float = 0.0
    y: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        
    def add_node(self, node: Node):
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.__dict__)
        
    def add_edge(self, source_id: str, target_id: str, edge_data: dict = None):
        if edge_data is None:
            edge_data = {}
        self.graph.add_edge(source_id, target_id, **edge_data)
        
        # Keep Node objects in sync with graph topology
        if source_id in self.nodes and target_id not in self.nodes[source_id].children:
            self.nodes[source_id].children.append(target_id)
        if target_id in self.nodes and source_id not in self.nodes[target_id].parents:
            self.nodes[target_id].parents.append(source_id)
            
    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
        
    def get_graph(self) -> nx.DiGraph:
        return self.graph
