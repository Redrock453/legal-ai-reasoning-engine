"""Swarm supervisor - manages multiple workers."""
import sys
import time
import threading
from task_queue import queue


def add_tasks(inputs: list[str]):
    task_ids = []
    for inp in inputs:
        tid = queue.add(inp)
        task_ids.append(tid)
        print(f"Added: {inp[:40]}...")
    return task_ids


def run_supervisor(task_inputs: list[str], num_workers: int = 3):
    print(f"\n=== SUPERVISOR ===")
    print(f"Tasks: {len(task_inputs)}")
    print(f"Workers: {num_workers}")
    
    add_tasks(task_inputs)
    
    threads = []
    for i in range(num_workers):
        wid = f"worker-{i+1}"
        from worker import run_worker_thread
        t = run_worker_thread(wid)
        threads.append(t)
        print(f"Started {wid}")
    
    print(f"\n=== RUNNING ===")
    
    while True:
        stats = queue.get_stats()
        print(f"Stats: pending={stats['pending']} running={stats['running']} done={stats['done']} failed={stats['failed']}")
        
        if stats['pending'] == 0 and stats['running'] == 0:
            break
        
        time.sleep(2)
    
    stats = queue.get_stats()
    print(f"\n=== DONE ===")
    print(f"Done: {stats['done']} | Failed: {stats['failed']}")
    
    return stats


if __name__ == "__main__":
    test_tasks = [
        "echo task 1",
        "echo task 2",
        "echo task 3",
    ]
    
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    
    run_supervisor(test_tasks, workers)