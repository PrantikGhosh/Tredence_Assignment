import uuid
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, Any

from app.engine.core import Graph
from app.registry import registry
from app.models import GraphCreateRequest, GraphRunRequest, GraphRunResponse, GraphStateResponse

# Import demos to register nodes
import app.demos.summarizer

app = FastAPI(title="Agent Workflow Engine")

# In-memory storage
graphs: Dict[str, Graph] = {}
runs: Dict[str, Dict[str, Any]] = {}

@app.post("/graph/create", response_model=Dict[str, str])
def create_graph(request: GraphCreateRequest):
    graph = Graph()
    
    # Add nodes
    for node_name in request.nodes:
        try:
            func = registry.get_node(node_name)
            graph.add_node(node_name, func)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Node '{node_name}' not registered")

    # Add linear edges
    for from_node, to_node in request.edges.items():
        try:
            graph.add_edge(from_node, to_node)
        except ValueError as e:
             raise HTTPException(status_code=400, detail=str(e))

    # Add conditional edges
    for from_node, config in request.conditional_edges.items():
        condition_name = config.get("condition")
        paths = config.get("paths", {})
        try:
            cond_func = registry.get_node(condition_name)
            graph.add_conditional_edges(from_node, cond_func, paths)
        except KeyError:
             raise HTTPException(status_code=400, detail=f"Condition Node '{condition_name}' not registered")
        except ValueError as e:
             raise HTTPException(status_code=400, detail=str(e))

    try:
        graph.set_entry_point(request.entry_point)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    graph_id = str(uuid.uuid4())
    graphs[graph_id] = graph
    return {"graph_id": graph_id}

async def execute_graph_task(run_id: str, graph: Graph, initial_state: Dict[str, Any]):
    try:
        runs[run_id]["status"] = "running"
        result = await graph.run(initial_state)
        runs[run_id]["status"] = "completed"
        runs[run_id]["final_state"] = result["final_state"]
        runs[run_id]["history"] = result["history"]
    except Exception as e:
        runs[run_id]["status"] = "failed"
        runs[run_id]["error"] = str(e)

@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest, background_tasks: BackgroundTasks):
    if request.graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph not found")

    graph = graphs[request.graph_id]
    run_id = str(uuid.uuid4())
    
    runs[run_id] = {
        "status": "pending",
        "initial_state": request.initial_state,
        "final_state": None,
        "history": []
    }
    
    # Run in background
    background_tasks.add_task(execute_graph_task, run_id, graph, request.initial_state)
    
    return GraphRunResponse(run_id=run_id, status="pending")

@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
def get_run_state(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_data = runs[run_id]
    
    # Construct partial state response
    # If running, we might not have 'final_state', so we return initial or empty
    # In a real system we'd peek at the live state, but here we just return what we have.
    current_state = run_data.get("final_state") or run_data.get("initial_state")
    
    return GraphStateResponse(
        run_id=run_id,
        status=run_data["status"],
        current_state=current_state,
        history=run_data.get("history", [])
    )

@app.get("/tools")
def list_tools():
    """Helper to see available nodes"""
    return {"tools": registry.list_nodes()}
