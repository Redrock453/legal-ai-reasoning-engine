"""PRODUCTION PIPELINE v1.0 - Graph-based legal reasoning with IMPROVE LOOP."""

from nodes.ares import run as ares_run
from nodes.admissibility import run as admissibility_run
from nodes.rag import run as rag_run
from nodes.advocate_graph import run as advocate_run
from nodes.scoring import run as scoring_run
from nodes.decision import run as decision_run
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_IMPROVE_ITERATIONS = 2


def run_single(task: str) -> dict:
    logger.info(f"Pipeline: {task}")
    
    facts_data = ares_run(task)
    logger.info(f"ARES: {len(facts_data.get('facts', []))} facts")
    
    admissibility = admissibility_run(
        facts_data.get("facts", []),
        facts_data.get("entities", []),
        task
    )
    logger.info(f"ADMISSIBILITY: risk={admissibility.get('risk_level', 0)}")
    
    admissible_facts = admissibility.get("admissible_facts", [])
    query = " ".join(admissible_facts) if admissible_facts else task
    if len(query) < 5:
        query = task
    
    tags = facts_data.get("entities", {}).get("constitutional", [])
    strategy = admissibility.get("search_strategy", "narrow")
    
    min_score = 0.25
     
    cases = rag_run(query, min_score=min_score, limit=10, tags=tags)
    
    if not cases:
        logger.warning("Empty RAG - retrying with broader search")
        cases = rag_run(task + " fourth amendment search", min_score=0.2, limit=15)
    
    logger.info(f"RAG: {len(cases)} cases")
    
    graph = advocate_run(
        task,
        admissible_facts,
        facts_data.get("violations", []),
        [{"id": c["id"], "payload": c["payload"]} for c in cases[:5]],
        admissibility
    )
    logger.info(f"ADVOCATE: graph built")
    
    score_data = scoring_run(graph, admissible_facts, admissibility, task)
    decision = decision_run(score_data)
    logger.info(f"DECISION: {decision} (score={score_data.get('overall_score', score_data.get('score'))})")
    
    return {
        "task": task,
        "facts": facts_data,
        "admissibility": admissibility,
        "cases": cases,
        "graph": graph,
        "score": score_data,
        "decision": decision
    }


def run(task: str, max_iterations: int = MAX_IMPROVE_ITERATIONS) -> dict:
    result = run_single(task)
    
    iteration = 0
    while decision_run(result["score"]) == "WEAK" and iteration < max_iterations:
        iteration += 1
        logger.info(f"IMPROVE LOOP iteration {iteration}")
        
        issues = result["score"].get("issues", [])
        fixes = result["score"].get("recommended_fixes", [])
        logger.info(f"Issues: {issues}, Fixes: {fixes}")
        
        retry_query = f"{task}. Address these issues: {issues}. Apply fixes: {fixes}"
        retry_result = run_single(retry_query)
        
        if decision_run(retry_result["score"]) == "OK":
            result = retry_result
            result["improved"] = True
            result["iterations"] = iteration
            break
        else:
            result = retry_result
            result["iterations"] = iteration
    
    if "improved" not in result:
        result["improved"] = False
        result["iterations"] = iteration
    
    return result


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "illegal search without warrant"
    result = run(task)
    print(f"\n=== {task} ===")
    print(f"Decision: {result['decision']}")
    print(f"Score: {result['score'].get('score')}")