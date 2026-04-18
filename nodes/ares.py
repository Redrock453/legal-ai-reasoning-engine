"""ARES node - decompose task into facts and violations."""
from llm import llm_json


PROMPT = """Extract facts and legal violations from the task.
Return JSON with:
- facts: list of factual elements
- violations: list of legal violations (constitutional, procedural, etc.)"""


def run(task: str) -> dict:
    return llm_json(PROMPT, task)