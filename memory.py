from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "cases"


def embed(text: str) -> list:
    return model.encode(text).tolist()


def search_cases(query: str, min_score: float = 0.3, limit: int = 10, tags: list = None) -> list:
    """Hybrid search: vector similarity + optional keyword filter."""
    
    query_embedding = embed(query)
    
    search_params = {
        "collection_name": COLLECTION,
        "limit": limit,
        "with_payload": True,
        "query": query_embedding
    }
    
    if tags:
        filter_query = models.Filter(
            must=[
                models.FieldCondition(
                    key="tags",
                    match=models.MatchAny(any=tags)
                )
            ]
        )
        search_params["query_filter"] = filter_query
        search_params["score_threshold"] = min_score * 0.7
    else:
        search_params["score_threshold"] = min_score
    
    try:
        results = client.query_points(**search_params)
    except Exception as e:
        logger.warning(f"Filtered search failed, falling back: {e}")
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
    
    if not cases:
        logger.warning(f"No cases found for query: {query}")
    
    return cases


def get_case_by_id(case_id: str) -> dict | None:
    """Retrieve single case by ID."""
    try:
        result = client.retrieve(
            collection_name=COLLECTION,
            ids=[case_id]
        )
        if result:
            return {
                "id": result[0].id,
                "score": 1.0,
                "payload": result[0].payload
            }
    except Exception as e:
        logger.error(f"Error getting case {case_id}: {e}")
    return None