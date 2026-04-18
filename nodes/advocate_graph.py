"""ADVOCATE GRAPH node - build IRAC structured legal argument."""
from llm import llm_json


PROMPT = """Build legal argument using IRAC structure (Issue, Rule, Application, Counterarguments).

Return JSON with:
- issue: The legal question to be resolved
- rule: The applicable constitutional/statutory rule with supporting precedent
- application: How the rule applies to the facts
- counterarguments: Potential counterarguments and replies
- conclusion: Final legal conclusion
- strength: 0.0-1.0 confidence in conclusion
- irac: Full IRAC structured analysis with:
  - issue: Clear statement of legal issue
  - rule: Specific rule with case citations
  - application: Application to facts
  - conclusion: Supported legal conclusion
- citations: List of case names used as authority
- precedent_analysis: How each precedent supports or undermines the argument

If evidence is weak (e.g., no warrant), acknowledge suppression risk.

Build a rigorous legal argument from facts through precedent to conclusion."""


def run(task: str, facts: list, violations: list, cases: list, admissibility: dict = None) -> dict:
    result = llm_json(PROMPT, str({
        "task": task,
        "facts": facts,
        "violations": violations,
        "cases": cases,
        "admissibility": admissibility or {}
    }))
    
    if "issue" not in result:
        result["issue"] = task
    if "conclusion" not in result:
        result["conclusion"] = "Inconclusive"
    if "strength" not in result:
        result["strength"] = 0.5
    
    return result