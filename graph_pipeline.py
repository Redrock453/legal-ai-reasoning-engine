"""PRODUCTION PIPELINE v1.0 - Graph-based legal reasoning."""

from nodes.ares import run as ares_run
from nodes.admissibility import run as admissibility_run
from nodes.rag import run as rag_run
from nodes.advocate_graph import run as advocate_run
from nodes.scoring import run as scoring_run
from nodes.decision import run as decision_run
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(task: str) -> dict:
    logger.info(f"Pipeline: {task}")
    
    facts_data = ares_run(task)
    logger.info(f"ARES: {len(facts_data.get('facts', []))} facts")
    
    admissibility = admissibility_run(
        facts_data.get("facts", []),
        task
    )
    logger.info(f"ADMISSIBILITY: risk={admissibility.get('risk_level', 0)}")
    
    admissible_facts = admissibility.get("admissible_facts", [])
    query = " ".join(admissible_facts) if admissible_facts else task
    
    cases = rag_run(query)
    logger.info(f"RAG: {len(cases)} cases")
    
    graph = advocate_run(
        task,
        admissible_facts,
        facts_data.get("violations", []),
        [{"id": c["id"], "payload": c["payload"]} for c in cases[:5]]
    )
    logger.info(f"ADVOCATE: {len(graph.get('nodes', []))} nodes")
    
    score_data = scoring_run(graph, admissible_facts, task)
    decision = decision_run(score_data)
    logger.info(f"DECISION: {decision} (score={score_data.get('score')})")
    
    return {
        "task": task,
        "facts": facts_data,
        "admissibility": admissibility,
        "cases": cases,
        "graph": graph,
        "score": score_data,
        "decision": decision
    }


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "illegal search without warrant"
    result = run(task)
    print(f"\n=== {task} ===")
    print(f"Decision: {result['decision']}")
    print(f"Score: {result['score'].get('score')}")