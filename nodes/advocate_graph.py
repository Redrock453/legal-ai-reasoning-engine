"""ADVOCATE GRAPH node - build structured argument graph."""
from llm import llm_json


PROMPT = """Build legal argument graph from facts and cases.

Return JSON with:
- nodes: [
    {
      "id": "n1",
      "claim": "claim text",
      "type": "fact" | "claim" | "precedent" | "rule"
    }
  ]
- edges: [
    {
      "from": "n1",
      "to": "n2",
      "relation": "supports" | "contradicts" | "extends"
    }
  ]
- final_position: final legal conclusion
- strength: 0.0-1.0 confidence
- citations: list of case names used

Build coherent argument chain from facts to conclusion."""


def run(task: str, facts: list, violations: list, cases: list) -> dict:
    return llm_json(PROMPT, str({
        "task": task,
        "facts": facts,
        "violations": violations,
        "cases": cases
    }))