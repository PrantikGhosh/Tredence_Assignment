from typing import Dict, Any, List
from app.registry import registry

@registry.register()
def split_text(state: Dict[str, Any]) -> Dict[str, Any]:
    text = state.get("text", "")
    # Simple split by newline for demo purposes
    chunks = [c for c in text.split("\n") if c.strip()]
    print(f"[{state.get('step', '?')}] Split text into {len(chunks)} chunks.")
    return {"chunks": chunks}

@registry.register()
def summarize_chunk(state: Dict[str, Any]) -> Dict[str, Any]:
    chunks = state.get("chunks", [])
    summaries = []
    # Mock summarization: take first 20 words to simulate a "summary"
    for chunk in chunks:
        summary = " ".join(chunk.split()[:20]) + "..."
        summaries.append(summary)
    print(f"[{state.get('step', '?')}] Generated summaries for {len(chunks)} chunks.")
    return {"summaries": summaries}

@registry.register()
def merge_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    summaries = state.get("summaries", [])
    merged = " ".join(summaries)
    print(f"[{state.get('step', '?')}] Merged summaries. Length: {len(merged)}")
    return {"current_summary": merged}

@registry.register()
def refine_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    current_summary = state.get("current_summary", "")
    # Mock refinement: remove the last word
    words = current_summary.split()
    if words:
        refined = " ".join(words[:-1])
    else:
        refined = ""
    print(f"[{state.get('step', '?')}] Refined summary. New length: {len(refined)}")
    return {"current_summary": refined}

@registry.register()
def should_refine(state: Dict[str, Any]) -> str:
    """
    Decides if we should refine further.
    Condition: if summary length > 250 chars, continue refining.
    """
    summary = state.get("current_summary", "")
    if len(summary) > 250:
        return "refine"
    return "stop"
