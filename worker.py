"""Worker agent for swarm execution."""
import sys
import time
import threading
from task_queue import queue, Task


WORKER_ID = "worker-1"


def run_worker(worker_id: str = WORKER_ID, max_iterations: int = None):
    iterations = 0
    
    print(f"[{worker_id}] Started")
    
    while True:
        task = queue.get_pending()
        
        if task is None:
            time.sleep(1)
            iterations += 1
            if max_iterations and iterations > max_iterations:
                print(f"[{worker_id}] No tasks, exiting")
                break
            continue
        
        print(f"[{worker_id}] Processing: {task.input[:50]}...")
        
        try:
            from agent_loop import run_agent
            result = run_agent(task.input)
            
            score = result.get("score", 0)
            queue.complete(task.id, result, score)
            
            print(f"[{worker_id}] Done - score: {score}")
            
        except Exception as e:
            print(f"[{worker_id}] Error: {e}")
            queue.fail(task.id, task.retries + 1)
        
        time.sleep(0.5)
    
    print(f"[{worker_id}] Stopped")


def run_worker_thread(worker_id: str = WORKER_ID):
    thread = threading.Thread(target=run_worker, args=(worker_id,))
    thread.daemon = True
    thread.start()
    return thread


if __name__ == "__main__":
    wid = sys.argv[1] if len(sys.argv) > 1 else WORKER_ID
    run_worker(wid)