import subprocess
import os
import json


MAX_RETRY = 2


def execute(task: str) -> dict:
    cmd = ["/root/.opencode/bin/opencode", "run", task]
    
    env = os.environ.copy()
    env["TERM"] = "dumb"
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        output = result.stdout + result.stderr
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": output,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "output": "", "returncode": -1}
    except Exception as e:
        return {"status": "error", "output": str(e), "returncode": -1}


def run_advocate(task: str, result: dict) -> dict:
    status = result.get("status", "error")
    output = result.get("output", "")
    
    if status == "timeout":
        return {"score": 0.0, "status": "FAIL", "issues": ["timeout"]}
    
    if status == "error":
        return {"score": 0.0, "status": "FAIL", "issues": [output[:200]]}
    
    error_markers = ["permission denied", "rejected permission", "failed", "error:", "cannot", "not found", "no such file"]
    for marker in error_markers:
        if marker.lower() in output.lower():
            return {"score": 0.3, "status": "FAIL", "issues": [f"found: {marker}"]}
    
    success_markers = ["done", "success", "completed", "created", "updated", "modified"]
    for marker in success_markers:
        if marker.lower() in output.lower():
            return {"score": 1.0, "status": "OK", "issues": []}
    
    if not output.strip():
        return {"score": 0.0, "status": "FAIL", "issues": ["empty output"]}
    
    return {"score": 0.7, "status": "OK", "issues": []}


def run_agent(task: str, max_retry: int = MAX_RETRY) -> dict:
    print(f"\n>>> AGENT: {task}")
    
    retry = 0
    last_result = None
    last_eval = None
    
    while retry <= max_retry:
        print(f"\n--- ITER {retry} ---")
        
        exec_result = execute(task)
        print(f"Exec status: {exec_result.get('status')}")
        
        evaluation = run_advocate(task, exec_result)
        print(f"Eval: {evaluation.get('status')} (score: {evaluation.get('score')})")
        
        last_result = exec_result
        last_eval = evaluation
        
        if evaluation.get("status") == "OK":
            output = exec_result.get("output", "")[:200]
            print(f"Output: {output}")
            return {
                "status": "DONE",
                "result": exec_result,
                "score": evaluation.get("score", 0),
                "iterations": retry + 1
            }
        
        if retry < max_retry:
            task = f"{task} (retry {retry + 1})"
            print(f"Retry with: {task}")
        
        retry += 1
    
    return {
        "status": "FAILED",
        "result": last_result,
        "score": last_eval.get("score", 0) if last_eval else 0,
        "iterations": retry,
        "issues": last_eval.get("issues", []) if last_eval else []
    }


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "echo hello"
    
    result = run_agent(task)
    print(f"\n=== FINAL ===")
    print(f"Status: {result.get('status')}")
    print(f"Score: {result.get('score')}")