from graph.builder import GraphBuilder, Node

class ConnectorOptimizer:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        self.graph = builder.get_graph()

    def optimize(self):
        """
        Calculates orthogonal waypoints for each edge in the graph.
        """
        for source_id, target_id, edge_data in self.graph.edges(data=True):
            source = self.builder.nodes[source_id]
            target = self.builder.nodes[target_id]
            
            # Source center-right
            start_x = source.x + source.metadata.get("width", 0)
            start_y = source.y + (source.metadata.get("height", 0) / 2)
            
            # Target center-left
            end_x = target.x
            end_y = target.y + (target.metadata.get("height", 0) / 2)
            
            # Default orthogonal routing (2 bend points)
            mid_x = start_x + (end_x - start_x) / 2
            
            waypoints = [
                (start_x, start_y),
                (mid_x, start_y),
                (mid_x, end_y),
                (end_x, end_y)
            ]
            
            # If target is visually behind source (e.g. loops or rejected flow)
            if end_x <= start_x:
                # Route from bottom of source to top of target
                start_x = source.x + (source.metadata.get("width", 0) / 2)
                start_y = source.y + source.metadata.get("height", 0)
                
                end_x = target.x + (target.metadata.get("width", 0) / 2)
                end_y = target.y
                
                # Simple loop around
                mid_y_source = start_y + 30
                mid_y_target = end_y - 30
                
                waypoints = [
                    (start_x, start_y),
                    (start_x, mid_y_source),
                    (end_x, mid_y_source),  # Might cross nodes, MVP simplified
                    (end_x, end_y)
                ]
            
            edge_data["waypoints"] = waypoints
