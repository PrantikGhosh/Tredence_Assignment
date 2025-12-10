from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GraphCreateRequest(BaseModel):
    nodes: List[str] = Field(..., description="List of node names (function names) to include")
    edges: Dict[str, str] = Field({}, description="Simple edges: from_node -> to_node")
    # For simplicity in this demo, we'll define conditional edges via a special structure
    # or just assume they are pre-wired if we were doing code-first.
    # BUT the prompt asks for "Input: JSON describing nodes and edges".
    # Let's support a basic conditional structure in JSON.
    conditional_edges: Dict[str, Dict[str, Any]] = Field(
        {}, 
        description="Map of from_node -> { 'condition': 'func_name', 'paths': { 'case': 'target' } }"
    )
    entry_point: str

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class GraphRunResponse(BaseModel):
    run_id: str
    status: str

class GraphStateResponse(BaseModel):
    run_id: str
    status: str
    current_state: Dict[str, Any]
    history: List[Dict[str, Any]]
