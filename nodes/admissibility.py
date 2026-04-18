"""ADMISSIBILITY node - filter facts for legal admissibility."""
from llm import llm_json


PROMPT = """Filter facts for legal admissibility.

Return JSON with:
- admissible_facts: facts that are legally admissible
- excluded_facts: facts that should be excluded
- exclusion_reasons: why each fact was excluded
- risk_level: 0.0 (clean) to 1.0 (toxic)
- search_strategy: "narrow" | "broad" | "suppressed-evidence"

Key rules:
- illegally obtained evidence → exclude
- hearsay → flag as risk
- coerced confession → exclude or flag
- facts without documentation → flag as risk"""


def run(facts: list, context: str) -> dict:
    return llm_json(PROMPT, str({"facts": facts, "context": context}))