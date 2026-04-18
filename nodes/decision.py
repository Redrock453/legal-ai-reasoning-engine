"""DECISION node - determine final output."""
from typing import Optional


THRESHOLD_OK = 0.8
THRESHOLD_WEAK = 0.5


def run(score: dict, threshold_ok: float = THRESHOLD_OK, threshold_weak: float = THRESHOLD_WEAK) -> str:
    score_value = score.get("overall_score", score.get("score", 0))
    
    if score_value >= threshold_ok:
        return "OK"
    elif score_value >= threshold_weak:
        return "WEAK"
    else:
        return "FAIL"


def get_score_value(score: dict) -> float:
    return score.get("overall_score", score.get("score", 0))


def should_retry(decision: str) -> bool:
    return decision == "WEAK"


def get_confidence(score: dict) -> float:
    return score.get("confidence", score.get("overall_score", 0))