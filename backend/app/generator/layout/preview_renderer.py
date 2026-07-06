from typing import Dict, List
from app.generator.layout.graph import LayoutNode, LayoutEdge
import html

class PreviewRenderer:
    def __init__(self, builder, layout_nodes: Dict[str, LayoutNode], layout_edges: List[LayoutEdge]):
        self.builder = builder
        self.nodes = layout_nodes
        self.edges = layout_edges
        
    def render_svg(self) -> str:
        svg_elements = []
        
        max_x = 0
        max_y = 0
        for lane_data in self.builder.graph.graph.get("lanes", {}).values():
            max_x = max(max_x, lane_data.get("x", 0) + lane_data.get("width", 1000))
            max_y = max(max_y, lane_data.get("y", 0) + lane_data.get("height", 200))
            
        canvas_width = max(800, max_x + 50)
        canvas_height = max(600, max_y + 50)
        
        svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}">')
        svg_elements.append('<style>')
        svg_elements.append('.lane { fill: none; stroke: #333; stroke-width: 2; }')
        svg_elements.append('.lane-title { font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #333; }')
        svg_elements.append('.task { fill: #dae8fc; stroke: #6c8ebf; stroke-width: 2; rx: 5; ry: 5; }')
        svg_elements.append('.gateway { fill: #fff2cc; stroke: #d6b656; stroke-width: 2; }')
        svg_elements.append('.start { fill: #d5e8d4; stroke: #82b366; stroke-width: 2; }')
        svg_elements.append('.end { fill: #f8cecc; stroke: #b85450; stroke-width: 3; }')
        svg_elements.append('.text { font-family: sans-serif; font-size: 12px; text-anchor: middle; dominant-baseline: middle; }')
        svg_elements.append('.edge { fill: none; stroke: #000; stroke-width: 1.5; }')
        svg_elements.append('.edge-label { font-family: sans-serif; font-size: 11px; fill: #555; background-color: white; }')
        svg_elements.append('</style>')
        
        svg_elements.append('''
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#000" />
            </marker>
        </defs>
        ''')
        
        for lane_name, data in self.builder.graph.graph.get("lanes", {}).items():
            lx, ly = data["x"], data["y"]
            lw, lh = data["width"], data["height"]
            svg_elements.append(f'<rect class="lane" x="{lx}" y="{ly}" width="{lw}" height="{lh}" />')
            
            svg_elements.append(f'<rect class="lane" x="{lx}" y="{ly}" width="40" height="{lh}" fill="#f5f5f5" />')
            
            text_x = lx + 20
            text_y = ly + lh / 2
            safe_name = html.escape(lane_name)
            svg_elements.append(f'<text class="lane-title" x="{text_x}" y="{text_y}" transform="rotate(-90, {text_x}, {text_y})" text-anchor="middle">{safe_name}</text>')

        for edge in self.edges:
            if not edge.waypoints:
                continue
            pts = edge.waypoints
            d = f"M {pts[0].x} {pts[0].y} "
            for pt in pts[1:]:
                d += f"L {pt.x} {pt.y} "
            svg_elements.append(f'<path class="edge" d="{d}" marker-end="url(#arrow)" />')
            
            if edge.label:
                mid_x = (pts[0].x + pts[1].x) / 2
                mid_y = (pts[0].y + pts[1].y) / 2
                if pts[0].y == pts[1].y:
                    mid_y -= 10
                else:
                    mid_x += 15
                svg_elements.append(f'<rect x="{mid_x-15}" y="{mid_y-8}" width="30" height="16" fill="white" />')
                svg_elements.append(f'<text class="edge-label" x="{mid_x}" y="{mid_y}">{html.escape(edge.label)}</text>')

        for node in self.nodes.values():
            bx = node.box.x
            by = node.box.y
            bw = node.box.width
            bh = node.box.height
            safe_label = html.escape(node.label or "")
            
            if node.type == "start":
                svg_elements.append(f'<circle class="start" cx="{bx + bw/2}" cy="{by + bh/2}" r="{bw/2}" />')
            elif node.type == "end":
                svg_elements.append(f'<circle class="end" cx="{bx + bw/2}" cy="{by + bh/2}" r="{bw/2}" />')
            elif node.type in ("exclusive_gateway", "parallel_gateway"):
                pts = f"{bx + bw/2},{by} {bx+bw},{by+bh/2} {bx+bw/2},{by+bh} {bx},{by+bh/2}"
                svg_elements.append(f'<polygon class="gateway" points="{pts}" />')
                if safe_label:
                    words = safe_label.split()
                    if len(words) > 2:
                        line1 = " ".join(words[:len(words)//2])
                        line2 = " ".join(words[len(words)//2:])
                        svg_elements.append(f'<text class="text" font-size="10" x="{bx + bw/2}" y="{by + bh/2 - 6}">{line1}</text>')
                        svg_elements.append(f'<text class="text" font-size="10" x="{bx + bw/2}" y="{by + bh/2 + 8}">{line2}</text>')
                    else:
                        svg_elements.append(f'<text class="text" font-size="10" x="{bx + bw/2}" y="{by + bh/2}">{safe_label}</text>')
            else:
                svg_elements.append(f'<rect class="task" x="{bx}" y="{by}" width="{bw}" height="{bh}" />')
                
                # Split label into words and wrap crudely
                words = safe_label.split()
                if len(words) > 2:
                    line1 = " ".join(words[:len(words)//2])
                    line2 = " ".join(words[len(words)//2:])
                    svg_elements.append(f'<text class="text" x="{bx + bw/2}" y="{by + bh/2 - 6}">{line1}</text>')
                    svg_elements.append(f'<text class="text" x="{bx + bw/2}" y="{by + bh/2 + 8}">{line2}</text>')
                else:
                    svg_elements.append(f'<text class="text" x="{bx + bw/2}" y="{by + bh/2}">{safe_label}</text>')
                
        svg_elements.append('</svg>')
        return "\n".join(svg_elements)
