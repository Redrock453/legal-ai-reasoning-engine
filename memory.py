from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "cases"


def embed(text: str) -> list:
    return model.encode(text).tolist()


def search_cases(query: str, min_score: float = 0.5, limit: int = 10) -> list:
    query_embedding = embed(query)
    
    results = client.query_points(
        collection_name=COLLECTION,
        query=query_embedding,
        limit=limit,
        score_threshold=min_score,
        with_payload=True
    )
    
    cases = []
    for r in results.points:
        cases.append({
            "id": r.id,
            "score": r.score,
            "payload": r.payload
        })
    
    return cases