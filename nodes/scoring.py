"""SCORING node - evaluate argument quality with multi-metric scoring."""
from llm import llm_json


PROMPT = """Evaluate legal argument quality across multiple dimensions.

Return JSON with:
- overall_score: 0.0-1.0 (weighted average)
- metrics: Detailed scoring:
  - logical_consistency: 0.0-1.0
  - precedent_alignment: 0.0-1.0
  - factual_grounding: 0.0-1.0
  - completeness: 0.0-1.0
  - rule_application: 0.0-1.0
- confidence: 0.0-1.0 (system confidence)
- issues: List of specific problems found
- recommended_fixes: Suggested improvements
- ok: true if overall_score >= 0.5

Evaluate:
1. IRAC structure present and coherent
2. Precedents properly applied to facts
3. Facts connected to conclusion
4. Counterarguments addressed
5. No missing legal elements"""


def run(graph: dict, facts: list, admissibility: dict, task: str) -> dict:
    result = llm_json(PROMPT, str({
        "graph": graph,
        "facts": facts,
        "admissibility": admissibility,
        "task": task
    }))
    
    if "metrics" not in result:
        result["metrics"] = {
            "logical_consistency": 0.5,
            "precedent_alignment": 0.5,
            "factual_grounding": 0.5,
            "completeness": 0.5,
            "rule_application": 0.5
        }
    if "overall_score" not in result:
        result["overall_score"] = result.get("score", 0.5)
    if "recommended_fixes" not in result:
        result["recommended_fixes"] = []
    if "issues" not in result:
        result["issues"] = []
    
    return result