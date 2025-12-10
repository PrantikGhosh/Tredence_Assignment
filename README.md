# Simple Agent Workflow Engine

A lightweight graph-based workflow engine built with Python and FastAPI. It supports defining workflows as graphs of nodes (functions) with state, conditional branching, and looping.

## Features
- **Nodes**: Regular Python functions that accept and return state updates.
- **Graph Engine**: Manages execution flow, state transitions, and history.
- **Branching & Looping**: Supports conditional logic and cycles in the graph.
- **Registry System**: Safely maps string names to Python functions for API usage.
- **FastAPI Endpoints**: Create and run graphs dynamically via JSON APIs.

## Project Structure
- `app/engine`: Core graph execution logic.
- `app/registry.py`: Decorator-based function registry.
- `app/demos`: Example workflow implementations.
- `app/main.py`: FastAPI application.
- `app/models.py`: Pydantic data models.
- `cli.py`: Interactive Command Line Interface.

## How to Run

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn requests
   ```

2. **Start the Server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Interact via CLI** (Recommended)
   In a new terminal:
   ```bash
   python cli.py
   ```
   This allows you to type in text and watch the agent split, summarize, and refine it in real-time.

## Example Workflow (Summarization Loop)
The included demo (`app/demos/summarizer.py`) implements:
1. `split_text`: Splits input into chunks.
2. `summarize_chunk`: "Summarizes" each chunk (takes first 20 words).
3. `merge_summaries`: Joins them back.
4. `refine_summary`: Iteratively removes words until the summary is short enough.
5. `should_refine`: Decides whether to loop back to refinement or stop (threshold: 250 chars).

## Future Improvements
- Persistent storage (SQL/NoSQL) not just in-memory.
- Proper async task queue (Celery/Redis) for robustness.
- Visualization UI to see the graph topology.
- More complex conditional logic and parallel node execution.
