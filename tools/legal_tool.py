"""Legal tool wrapper for open-code runtime."""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def legal_tool(task: str) -> dict:
    """
    Wrapper for Legal Reasoning Graph.
    Input: raw user task
    Output: structured legal decision
    """
    try:
        from graph_pipeline import run
        
        result = run(task)
        
        return {
            "decision": result.get("decision", "UNKNOWN"),
            "score": result.get("score", {}).get("overall_score", result.get("score", {}).get("score", 0)),
            "cases_count": len(result.get("cases", [])),
            "graph_nodes": len(result.get("graph", {}).get("nodes", [])),
            "issues": result.get("score", {}).get("issues", [])[:3],
            "status": "ok"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


if __name__ == "__main__":
    test = "police entered home without warrant"
    result = legal_tool(test)
    print(f"Legal tool: {result.get('status')}")
    print(f"Decision: {result.get('decision')}")
    print(f"Score: {result.get('score')}")