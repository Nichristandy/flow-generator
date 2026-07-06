from parser.ast import FlowAst, AstStart, AstEnd, AstTask, AstIf, AstElse, AstEndIf
from graph.builder import GraphBuilder, Node
import uuid

def generate_id() -> str:
    return "id_" + uuid.uuid4().hex[:8]

class AstCompiler:
    def __init__(self, ast: FlowAst):
        self.ast = ast
        self.builder = GraphBuilder()

    def compile(self) -> GraphBuilder:
        current_nodes = []
        branch_stack = []
        name_to_node_id = {}
        deferred_gotos = []
        
        def add_edges_from_current(target_id: str):
            for src in current_nodes:
                label = ""
                if branch_stack:
                    state = branch_stack[-1]
                    if src == state["gateway"]:
                        if not state["in_else"] and not state.get("if_started"):
                            label = "Yes"
                            state["if_started"] = True
                        elif state["in_else"] and not state.get("else_started"):
                            label = "No"
                            state["else_started"] = True
                
                self.builder.add_edge(src, target_id, {"label": label} if label else {})
        
        for ast_node in self.ast.nodes:
            if isinstance(ast_node, AstStart):
                node = Node(id=generate_id(), label="", actor="System", lane="System", type="start")
                self.builder.add_node(node)
                current_nodes = [node.id]
                
            elif isinstance(ast_node, AstEnd):
                node = Node(id=generate_id(), label="", actor="System", lane="System", type="end")
                self.builder.add_node(node)
                add_edges_from_current(node.id)
                current_nodes = []
                
            elif isinstance(ast_node, AstTask):
                node = Node(id=generate_id(), label=ast_node.name, actor=ast_node.actor, lane=ast_node.actor, type="task")
                self.builder.add_node(node)
                name_to_node_id[ast_node.name] = node.id
                add_edges_from_current(node.id)
                current_nodes = [node.id]
                
            elif isinstance(ast_node, AstIf):
                # Gateway node
                gw_lane = "System"
                if current_nodes:
                    parent_node = self.builder.get_node(current_nodes[0])
                    if parent_node:
                        gw_lane = parent_node.lane
                        
                node = Node(id=generate_id(), label=f"{ast_node.condition}?", actor="System", lane=gw_lane, type="exclusive_gateway")
                self.builder.add_node(node)
                add_edges_from_current(node.id)
                
                # Push state
                branch_stack.append({
                    "gateway": node.id,
                    "condition": ast_node.condition,
                    "if_ends": [],
                    "else_ends": [],
                    "in_else": False
                })
                current_nodes = [node.id]
                
            elif isinstance(ast_node, AstElse):
                if branch_stack:
                    # Save the ends of the IF branch
                    branch_stack[-1]["if_ends"] = current_nodes
                    branch_stack[-1]["in_else"] = True
                    # Reset current_nodes to the gateway
                    current_nodes = [branch_stack[-1]["gateway"]]
                    
            elif isinstance(ast_node, AstEndIf):
                if branch_stack:
                    state = branch_stack.pop()
                    if state["in_else"]:
                        state["else_ends"] = current_nodes
                    else:
                        state["if_ends"] = current_nodes
                        
                    # Merge gateway
                    gw_lane = "System"
                    if state["if_ends"]:
                        parent_node = self.builder.get_node(state["if_ends"][0])
                        if parent_node:
                            gw_lane = parent_node.lane
                    elif state["else_ends"]:
                        parent_node = self.builder.get_node(state["else_ends"][0])
                        if parent_node:
                            gw_lane = parent_node.lane
                            
                    merge_gw = Node(id=generate_id(), label="", actor="System", lane=gw_lane, type="exclusive_gateway")
                    self.builder.add_node(merge_gw)
                    
                    if state["if_ends"]:
                        for src in state["if_ends"]:
                            # If the source is the gateway itself and we haven't started, it needs a label
                            label = ""
                            if src == state["gateway"] and not state.get("if_started"):
                                label = "Yes"
                            self.builder.add_edge(src, merge_gw.id, {"label": label} if label else {})
                            
                    if state["else_ends"]:
                        for src in state["else_ends"]:
                            label = ""
                            if src == state["gateway"] and not state.get("else_started"):
                                label = "No"
                            self.builder.add_edge(src, merge_gw.id, {"label": label} if label else {})
                    elif not state["else_ends"] and not state.get("else_is_goto"):
                        # Implicit empty else, unless it was a goto
                        self.builder.add_edge(state["gateway"], merge_gw.id, {"label": "No"})
                        
                    current_nodes = [merge_gw.id]
                    
            elif type(ast_node).__name__ == "AstGoto":
                # For AstGoto, connect all current_nodes to the target
                # Check if target is already known
                target_name = ast_node.target
                label = ""
                # If the source is the gateway itself, label it
                if branch_stack:
                    state = branch_stack[-1]
                    if current_nodes == [state["gateway"]]:
                        label = "No" if state["in_else"] else "Yes"
                        if state["in_else"]:
                            state["else_is_goto"] = True
                        else:
                            state["if_is_goto"] = True
                
                for src in current_nodes:
                    deferred_gotos.append((src, target_name, label))
                
                # A GOTO ends the current path
                current_nodes = []

        # Process deferred GOTO edges
        for src, target_name, label in deferred_gotos:
            if target_name in name_to_node_id:
                self.builder.add_edge(src, name_to_node_id[target_name], {"label": label})
            else:
                # If target not found, create a dummy end node for it or raise an error
                # For robustness, create a node
                node = Node(id=generate_id(), label=target_name, actor="System", lane="System", type="end")
                self.builder.add_node(node)
                name_to_node_id[target_name] = node.id
                self.builder.add_edge(src, node.id, {"label": label})
                    
        return self.builder
