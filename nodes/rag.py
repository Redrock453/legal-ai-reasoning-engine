"""RAG node - retrieve similar cases."""
from memory import search_cases


def run(query: str, min_score: float = 0.5) -> list:
    return search_cases(query, min_score)