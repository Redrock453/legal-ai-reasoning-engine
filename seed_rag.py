#!/usr/bin/env python3
"""Seed Qdrant with legal cases."""
import json
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLLECTION = "cases"


def build_text(case):
    return f"""
Title: {case['title']}
Principle: {case['principle']}
Facts: {case['facts']}
Holding: {case['holding']}
Tags: {', '.join(case['tags'])}
""".strip()


def embed(texts, model):
    return model.encode(texts).tolist()


def seed_cases():
    logger.info("Loading cases...")
    with open("data/cases_seed.json") as f:
        cases = json.load(f)
    
    logger.info(f"Loaded {len(cases)} cases")
    
    logger.info("Loading embeddings model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    logger.info("Connecting to Qdrant...")
    client = QdrantClient(url="http://localhost:6333")
    
    logger.info(f"Checking collection '{COLLECTION}'...")
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION for c in collections)
    
    if exists:
        logger.info(f"Deleting existing '{COLLECTION}'...")
        client.delete_collection(COLLECTION)
    
    logger.info(f"Creating collection '{COLLECTION}'...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={"size": 384, "distance": "Cosine"}
    )
    
    logger.info("Building embeddings...")
    texts = [build_text(c) for c in cases]
    vectors = embed(texts, model)
    
    logger.info("Uploading to Qdrant...")
    points = [
        {
            "id": i,
            "vector": vectors[i],
            "payload": cases[i]
        }
        for i in range(len(cases))
    ]
    
    client.upsert(
        collection_name=COLLECTION,
        points=points
    )
    
    logger.info(f"Seeded {len(cases)} cases")
    
    print(f"\n✅ Done: {len(cases)} cases in Qdrant")
    
    logger.info("Verifying...")
    count = client.count(collection_name=COLLECTION).count
    print(f"Total in collection: {count}")


if __name__ == "__main__":
    seed_cases()