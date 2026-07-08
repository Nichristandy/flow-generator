from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Union

class TaskNode(BaseModel):
    id: str = Field(..., description="A unique identifier for this node, e.g., 'task_1'")
    type: Literal["task"] = "task"
    actor: str = Field(..., description="The person, system, or role performing the task")
    description: str = Field(..., description="The action being performed")
    next: Optional[List[str]] = Field(default_factory=list, description="IDs of the next nodes in the flow")

class ConditionNode(BaseModel):
    id: str = Field(..., description="A unique identifier for this gateway")
    type: Literal["condition"] = "condition"
    description: str = Field(..., description="The question or condition being evaluated, e.g., 'Is approved?'")
    paths: Dict[str, List[str]] = Field(..., description="A mapping of outcomes (e.g., 'Yes', 'No') to the IDs of the first node in that path")

class LoopNode(BaseModel):
    id: str = Field(..., description="A unique identifier for this loop target")
    type: Literal["loop_target"] = "loop_target"
    name: str = Field(..., description="The label or name of this loop target, e.g., 'Re-approval Loop'")
    next: Optional[List[str]] = Field(default_factory=list, description="IDs of the next nodes in the flow")

class ParallelNode(BaseModel):
    id: str = Field(..., description="A unique identifier for this parallel gateway")
    type: Literal["parallel"] = "parallel"
    branches: List[List[str]] = Field(..., description="A list of branches, where each branch is a list of node IDs starting that branch")

# We use a discriminated union if needed, but for simple schema parsing, we can just use a generic Node or Union
FlowNode = Union[TaskNode, ConditionNode, LoopNode, ParallelNode]

class FlowJSON(BaseModel):
    title: str = Field(default="Business Process Flow", description="The title of the process")
    nodes: Dict[str, FlowNode] = Field(..., description="A dictionary mapping node IDs to their node definitions")
    start_node: str = Field(..., description="The ID of the node where the process begins")
