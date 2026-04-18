"""Shared task queue for swarm execution."""
import threading
import uuid
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    input: str = ""
    status: str = "pending"  # pending, running, done, failed
    worker_id: Optional[str] = None
    result: Optional[dict] = None
    score: float = 0.0
    retries: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class TaskQueue:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._lock = threading.Lock()
    
    def add(self, task_input: str) -> str:
        task = Task(input=task_input)
        with self._lock:
            self._tasks[task.id] = task
        return task.id
    
    def get_pending(self) -> Optional[Task]:
        with self._lock:
            for task in self._tasks.values():
                if task.status == "pending":
                    task.status = "running"
                    task.updated_at = time.time()
                    return task
        return None
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def complete(self, task_id: str, result: dict, score: float):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = "done"
                self._tasks[task_id].result = result
                self._tasks[task_id].score = score
                self._tasks[task_id].updated_at = time.time()
    
    def fail(self, task_id: str, retries: int = 0):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].retries = retries
                if retries >= 3:
                    self._tasks[task_id].status = "failed"
                else:
                    self._tasks[task_id].status = "pending"
                self._tasks[task_id].updated_at = time.time()
    
    def get_stats(self) -> dict:
        pending = running = done = failed = 0
        with self._lock:
            for t in self._tasks.values():
                if t.status == "pending":
                    pending += 1
                elif t.status == "running":
                    running += 1
                elif t.status == "done":
                    done += 1
                elif t.status == "failed":
                    failed += 1
        return {
            "pending": pending,
            "running": running,
            "done": done,
            "failed": failed,
            "total": len(self._tasks)
        }


queue = TaskQueue()