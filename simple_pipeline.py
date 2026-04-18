from llm import llm_json
from memory import search_cases
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PROMPT_ARES = """Extract facts and legal violations from the task.
Return JSON with:
- facts: list of factual elements
- violations: list of legal violations (constitutional, procedural, etc.)"""

PROMPT_ADMISSIBILITY = """Filter facts for legal admissibility.
For each fact, determine if it can be used in court proceedings.

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

PROMPT_ADVOCATE_GRAPH = """Build legal argument graph from facts and cases.

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

PROMPT_SCORING_GRAPH = """Evaluate argument graph quality.

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


def run(task: str) -> dict:
    logger.info(f"Processing task: {task}")
    
    # 1. ARES - Extract facts + violations
    logger.info("Step 1: ARES extraction")
    facts_data = llm_json(PROMPT_ARES, task)
    logger.info(f"Extracted facts: {facts_data.get('facts', [])}")
    logger.info(f"Extracted violations: {facts_data.get('violations', [])}")
    
    # 2. ADMISSIBILITY - Filter facts
    logger.info("Step 2: ADMISSIBILITY filter")
    admissibility_input = {
        "facts": facts_data.get("facts", []),
        "context": task
    }
    admissibility = llm_json(PROMPT_ADMISSIBILITY, str(admissibility_input))
    logger.info(f"Admissible: {len(admissibility.get('admissible_facts', []))}")
    logger.info(f"Excluded: {len(admissibility.get('excluded_facts', []))}")
    logger.info(f"Risk level: {admissibility.get('risk_level', 0)}")
    
    # 3. RAG - Search similar cases (using admissible facts ONLY)
    logger.info("Step 3: RAG search")
    
    admissible_facts = admissibility.get("admissible_facts", [])
    if admissible_facts:
        query = " ".join(admissible_facts)
    else:
        violations = facts_data.get("violations", [])
        if violations and isinstance(violations[0], dict):
            query = " ".join([v.get("description", "") or v.get("provision", "") for v in violations])
        else:
            query = " ".join(violations)
        if not query:
            query = task
    
    cases = search_cases(query, min_score=0.5)
    
    if len(cases) == 0:
        logger.warning("RAG returned no cases")
    
    logger.info(f"RAG returned {len(cases)} cases")
    for i, c in enumerate(cases):
        logger.info(f"  Case {i+1}: score={c['score']:.3f}")
    
    # 4. ADVOCATE - Build argument graph
    logger.info("Step 4: ADVOCATE graph")
    advocate_input = {
        "task": task,
        "facts": admissibility.get("admissible_facts", []),
        "violations": facts_data.get("violations", []),
        "cases": [{"id": c["id"], "payload": c["payload"]} for c in cases[:5]]
    }
    graph = llm_json(PROMPT_ADVOCATE_GRAPH, str(advocate_input))
    logger.info(f"Graph: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges")
    logger.info(f"Position: {graph.get('final_position')}")
    logger.info(f"Strength: {graph.get('strength', 0)}")
    
    # 5. SCORING - Evaluate graph quality
    logger.info("Step 5: GRAPH SCORING")
    scoring_input = {
        "graph": graph,
        "facts": admissibility.get("admissible_facts", []),
        "task": task
    }
    score_data = llm_json(PROMPT_SCORING_GRAPH, str(scoring_input))
    logger.info(f"Score: {score_data.get('score', 0)}")
    
    # 5. DECISION
    score = score_data.get("score", 0)
    if score >= 0.8:
        decision = "OK"
    elif score >= 0.5:
        decision = "WEAK"
    else:
        decision = "FAIL"
    
    logger.info(f"Decision: {decision}")
    
    return {
        "facts": facts_data,
        "admissibility": admissibility,
        "cases": cases,
        "graph": graph,
        "score": score_data,
        "decision": decision
    }