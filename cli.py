import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def create_summarizer_graph():
    payload = {
        "nodes": [
            "split_text", 
            "summarize_chunk", 
            "merge_summaries", 
            "refine_summary", 
            "should_refine"
        ],
        "edges": {
            "split_text": "summarize_chunk",
            "summarize_chunk": "merge_summaries",
            "merge_summaries": "refine_summary"
        },
        "conditional_edges": {
            "refine_summary": {
                "condition": "should_refine",
                "paths": {
                    "refine": "refine_summary", 
                    "stop": "__END__"
                }
            }
        },
        "entry_point": "split_text"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/graph/create", json=payload)
        resp.raise_for_status()
        return resp.json()["graph_id"]
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the server is running: python -m uvicorn app.main:app")
        sys.exit(1)

def run_interaction():
    print("--- Agent Workflow Engine CLI ---")
    
    # 1. Ensure Graph Exists for this session
    print("Initializing Graph...")
    graph_id = create_summarizer_graph()
    print(f"Graph initialized (ID: {graph_id})")
    
    while True:
        print("\n" + "="*40)
        print("Enter text to summarize (or type 'quit' to exit):")
        print("="*40)
        
        user_input = input("> ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break
            
        if not user_input:
            continue

        print(f"\nProcessing job for input of length {len(user_input)}...")
        
        # 2. Start Run
        try:
            resp = requests.post(f"{BASE_URL}/graph/run", json={
                "graph_id": graph_id, 
                "initial_state": {"text": user_input}
            })
            resp.raise_for_status()
            run_id = resp.json()["run_id"]
        except Exception as e:
            print(f"Failed to start run: {e}")
            continue
            
        # 3. Poll
        waiting_chars = ["|", "/", "-", "\\"]
        idx = 0
        while True:
            resp = requests.get(f"{BASE_URL}/graph/state/{run_id}")
            data = resp.json()
            status = data["status"]
            
            sys.stdout.write(f"\rStatus: {status} {waiting_chars[idx % 4]}")
            sys.stdout.flush()
            idx += 1
            
            if status in ["completed", "failed"]:
                print("\n")
                if status == "completed":
                    final_state = data.get("current_state", {})
                    history = data.get("history", [])
                    
                    print(f"\nExecution Trace ({len(history)} steps):")
                    for step in history:
                        print(f" -> {step['node']}")
                    
                    print("\n--- Final Summary ---")
                    print(final_state.get("current_summary", "No summary produced"))
                    print("---------------------")
                else:
                    print("Workflow Failed.")
                break
            
            time.sleep(0.5)

if __name__ == "__main__":
    run_interaction()
