"""ADMISSIBILITY node - filter facts for legal admissibility with suppression logic."""
from llm import llm_json


PROMPT = """Analyze facts for legal admissibility and suppression issues.

Return JSON with:
- admissible_facts: legally admissible facts (properly obtained, documented)
- excluded_facts: facts that must be excluded
- exclusion_reasons: legal basis for each exclusion (e.g., "fruit of poisonous tree", "hearsay")
- risk_flags: list of issues requiring attention:
  - warrantless_search: evidence obtained without warrant
  - coerced_confession: involuntary statement
  - hearsay: out-of-court statement offered for truth
  - improper_lineup: suggestive identification procedure
  - lack_of_documentation: facts without corroboration
  - unauthorized_interception: wiretap without order
- risk_level: 0.0 (clean) to 1.0 (high risk of suppression)
- search_strategy: "narrow" | "broad" | "suppressed-evidence" - how to structure RAG query
- suppression_warning: true if evidence likely to be suppressed

Key Rules:
1. Evidence obtained in violation of 4th Amendment → Exclude (Mapp v. Ohio)
2. Coerced confessions → Exclude (Colorado v. Connelly)
3. Unconstitutional lineup → Exclude or flag as tainted
4. Hearsay without exception → Flag
5. Fruit of poisonous tree → Exclude
6. Missing chain of custody → Flag as risk"""


def run(facts: list, entities: dict, context: str) -> dict:
    result = llm_json(PROMPT, str({
        "facts": facts,
        "entities": entities,
        "context": context
    }))
    
    if "search_strategy" not in result:
        result["search_strategy"] = "narrow"
    if "suppression_warning" not in result:
        result["suppression_warning"] = False
    
    return result