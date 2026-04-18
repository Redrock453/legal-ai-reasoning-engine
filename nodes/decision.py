"""DECISION node - determine final output."""
from typing import Optional


THRESHOLD_OK = 0.8
THRESHOLD_WEAK = 0.5


def run(score: dict, threshold_ok: float = THRESHOLD_OK, threshold_weak: float = THRESHOLD_WEAK) -> str:
    score_value = score.get("score", 0)
    
    if score_value >= threshold_ok:
        return "OK"
    elif score_value >= threshold_weak:
        return "WEAK"
    else:
        return "FAIL"


def should_retry(decision: str) -> bool:
    return decision == "WEAK"