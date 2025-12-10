import asyncio
from typing import Callable, Dict, Any, Optional, List, Union
import inspect

# Type aliases
State = Dict[str, Any]
NodeFunction = Callable[[State], Union[State, Dict[str, Any]]]
ConditionFunction = Callable[[State], str]

class GraphExecutionError(Exception):
    pass

class Graph:
    def __init__(self):
        self.nodes: Dict[str, NodeFunction] = {}
        self.edges: Dict[str, str] = {}
        self.branches: Dict[str, tuple[ConditionFunction, Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None
        self.end_point: str = "__END__"

    def add_node(self, name: str, func: NodeFunction):
        self.nodes[name] = func

    def set_entry_point(self, node_name: str):
        if node_name not in self.nodes:
            raise ValueError(f"Node {node_name} not found")
        self.entry_point = node_name

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.nodes:
             raise ValueError(f"Source node {from_node} not found")
        # to_node can be __END__
        if to_node != self.end_point and to_node not in self.nodes:
             raise ValueError(f"Target node {to_node} not found")
        
        self.edges[from_node] = to_node

    def add_conditional_edges(self, 
                              from_node: str, 
                              condition: ConditionFunction, 
                              path_map: Dict[str, str]):
        """
        Adds a conditional edge.
        condition(state) -> returns a string key (e.g., "continue", "stop")
        path_map -> maps that key to the next node name. 
        """
        if from_node not in self.nodes:
             raise ValueError(f"Source node {from_node} not found")
        
        for target in path_map.values():
            if target != self.end_point and target not in self.nodes:
                raise ValueError(f"Target node {target} not found")

        self.branches[from_node] = (condition, path_map)

    async def run(self, initial_state: State) -> list[Dict[str, Any]]:
        """
        Runs the graph. Returns a history of steps.
        History format: [{"node": "name", "state": {...}}, ...]
        """
        if not self.entry_point:
            raise GraphExecutionError("No entry point defined")

        current_node = self.entry_point
        state = initial_state.copy()
        history = []
        
        # Limit max steps to prevent infinite loops during dev
        max_steps = 100 
        steps = 0

        while current_node != self.end_point and steps < max_steps:
            steps += 1
            node_func = self.nodes[current_node]
            
            # Execute node
            try:
                if inspect.iscoroutinefunction(node_func):
                    result = await node_func(state)
                else:
                    result = node_func(state)
            except Exception as e:
                raise GraphExecutionError(f"Error in node {current_node}: {str(e)}")

            # Update state - request said "modifies a shared state"
            # We assume the functions might return a full new state or a dict to update
            if isinstance(result, dict):
                state.update(result)
            
            history.append({
                "step": steps,
                "node": current_node,
                "state": state.copy()  # Snapshot
            })

            # Determine next node
            if current_node in self.branches:
                condition_func, path_map = self.branches[current_node]
                try:
                    # Condition might need state to decide
                    if inspect.iscoroutinefunction(condition_func):
                         branch_key = await condition_func(state)
                    else:
                         branch_key = condition_func(state)
                except Exception as e:
                     raise GraphExecutionError(f"Error evaluating condition at {current_node}: {str(e)}")
                
                if branch_key not in path_map:
                     raise GraphExecutionError(f"Condition returned '{branch_key}' which is not in path_map for {current_node}")
                
                current_node = path_map[branch_key]
            
            elif current_node in self.edges:
                current_node = self.edges[current_node]
            else:
                # No outgoing edge means we stop? Or implicit end?
                # Let's assume implicit end if no edge defined.
                current_node = self.end_point

        return {"final_state": state, "history": history}
