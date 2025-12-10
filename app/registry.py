from typing import Callable, Dict, Any

class NodeRegistry:
    def __init__(self):
        self._nodes: Dict[str, Callable] = {}

    def register(self, name: str = None):
        """Decorator to register a function as a node."""
        def decorator(func: Callable):
            key = name or func.__name__
            self._nodes[key] = func
            return func
        return decorator

    def get_node(self, name: str) -> Callable:
        """Retrieve a node function by name."""
        if name not in self._nodes:
            raise KeyError(f"Node '{name}' not found in registry.")
        return self._nodes[name]

    def list_nodes(self):
        return list(self._nodes.keys())

# Global registry instance
registry = NodeRegistry()
