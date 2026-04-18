"""ARES node - decompose task into facts, violations and entities."""
from llm import llm_json


PROMPT = """Analyze the legal task and extract structured elements.

Return JSON with:
- facts: list of legally relevant factual elements (who, what, when, where, how)
- violations: list of legal violations (4th amendment, 5th amendment, Miranda, etc.)
- entities: list of extracted entities:
  - persons: defendants, officers, witnesses, victims
  - locations: addresses, property types (home, vehicle, business)
  - dates: dates and times mentioned
  - evidence: physical evidence, documents, statements
  - constitutional: amendments, rights, clauses
- legal_issues: list of legal issues to resolve
- jurisdiction: implied jurisdiction if any

Be precise and extract all entities that could be relevant to building a legal argument."""


def run(task: str) -> dict:
    result = llm_json(PROMPT, task)
    if "entities" not in result:
        result["entities"] = []
    if "legal_issues" not in result:
        result["legal_issues"] = []
    if "jurisdiction" not in result:
        result["jurisdiction"] = None
    return result