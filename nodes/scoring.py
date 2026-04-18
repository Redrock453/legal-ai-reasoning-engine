"""SCORING node - evaluate argument graph quality."""
from llm import llm_json


PROMPT = """Evaluate argument graph quality.

Return JSON with:
- score: 0-1 (graph consistency)
- issues: list of graph problems
- missing_nodes: nodes that should exist
- weak_edges: edges with weak support
- ok: true if score >= 0.5

Check:
- all facts connected to conclusion
- precedents support claims
- no missing critical links"""


def run(graph: dict, facts: list, task: str) -> dict:
    return llm_json(PROMPT, str({
        "graph": graph,
        "facts": facts,
        "task": task
    }))