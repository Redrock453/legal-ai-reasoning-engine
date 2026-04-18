from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from graph_pipeline import run
import logging
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codex_loop import run_stream
from memory import client as qdrant_client
from llm import client as llm_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Legal AI Reasoning Engine v1.0")


class TaskRequest(BaseModel):
    task: str


class TaskResponse(BaseModel):
    decision: str
    score: float
    confidence: float
    metrics: dict
    cases_found: int
    iterations: int
    improved: bool


@app.post("/pipeline/run", response_model=TaskResponse)
def run_pipeline(req: TaskRequest):
    logger.info(f"Request: {req.task}")
    try:
        result = run(req.task)
        return {
            "decision": result.get("decision"),
            "score": result.get("score", {}).get("overall_score", result.get("score", {}).get("score", 0)),
            "confidence": result.get("score", {}).get("confidence", 0),
            "metrics": result.get("score", {}).get("metrics", {}),
            "cases_found": len(result.get("cases", [])),
            "iterations": result.get("iterations", 0),
            "improved": result.get("improved", False)
        }
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/run/verbose")
def run_pipeline_verbose(req: TaskRequest):
    logger.info(f"Request (verbose): {req.task}")
    try:
        result = run(req.task)
        return result
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.get("/health")
def health():
    """Check system health."""
    status = {"status": "ok", "components": {}}
    
    try:
        qdrant_client.get_collections()
        status["components"]["qdrant"] = "ok"
    except Exception as e:
        status["components"]["qdrant"] = f"error: {e}"
        status["status"] = "degraded"
    
    try:
        llm_client.models.list()
        status["components"]["llm"] = "ok"
    except Exception as e:
        status["components"]["llm"] = f"error: {e}"
        status["status"] = "degraded"
    
    return status


@app.get("/ready")
def ready():
    """Check if system is ready to accept requests."""
    try:
        qdrant_client.get_collections()
        return {"ready": True}
    except Exception:
        return {"ready": False}


@app.get("/metrics")
def metrics():
    """System metrics."""
    return {
        "version": "1.0",
        "pipeline": "graph-based",
        "rag": "hybrid",
        "improve_loop": True,
        "decision_thresholds": {"ok": 0.8, "weak": 0.5}
    }


@app.get("/run/stream")
def run_stream_api(goal: str):
    def event_generator():
        for event in run_stream(goal):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)