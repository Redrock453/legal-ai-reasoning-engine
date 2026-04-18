"""RAG node - retrieve similar cases."""
from memory import search_cases


def run(query: str, min_score: float = 0.3, limit: int = 10, tags: list = None) -> list:
    return search_cases(query, min_score=min_score, limit=limit, tags=tags)