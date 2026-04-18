# LEGAL AI SYSTEM v1.0

## Pipeline Flow
```
ARES → ADMISSIBILITY → RAG → ADVOCATE GRAPH → SCORING → DECISION
```

## Core State
```json
{
  "task": "string",
  "facts": [],
  "admissibility": {"admissible_facts": [], "risk_level": 0.0},
  "cases": [],
  "graph": {"nodes": [], "edges": []},
  "score": 0.0,
  "decision": "OK | WEAK | FAIL"
}
```

## Metrics
- Pipeline: OK
- RAG: needs cases (0 returned in test)
- Graph Advocate: 11 nodes working
- Decision threshold: 0.8 OK / 0.5 WEAK / <0.5 FAIL

## Decision Rules
- score >= 0.8 → OK
- score >= 0.5 → WEAK (retry once)
- score < 0.5 → FAIL