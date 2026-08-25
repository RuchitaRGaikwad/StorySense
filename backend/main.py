#!/usr/bin/env python3
"""
main.py — FastAPI application for StorySense recommendation engine.

Endpoints:
    GET /api/health              — Health check
    GET /api/content             — Search/autocomplete
    GET /api/content/{content_id}— Item detail
    GET /api/recommend/{content_id} — Recommendations
    GET /api/evaluate            — Evaluation metrics
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from recommend import get_engine

app = FastAPI(
    title="StorySense API",
    description="NLP-based cross-media recommendation engine using sentence-transformer embeddings and cosine similarity.",
    version="0.1.0",
)

# Allow CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Load the recommendation engine on startup."""
    get_engine()


@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "StorySense API", "version": "0.1.0"}


@app.get("/api/content")
def search_content(
    query: str = Query(..., min_length=1, description="Search query"),
    media_type: Optional[str] = Query(None, description="Filter by media type (movie, tv, book, or all)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """
    Search/autocomplete over the dataset.
    Matches query against title and description fields.
    """
    engine = get_engine()
    results = engine.search(query=query, media_type=media_type, limit=limit)
    return {"query": query, "results": results, "count": len(results)}


@app.get("/api/content/{content_id}")
def get_content(content_id: str):
    """Get a single item by content_id."""
    engine = get_engine()
    item = engine.get_item(content_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item '{content_id}' not found")
    return item


@app.get("/api/recommend/{content_id}")
def get_recommendations(
    content_id: str,
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    target_media: Optional[str] = Query(None, description="Target media types (comma-separated: book,tv,movie)"),
    include_same_media: bool = Query(False, description="Include items of the same media type"),
):
    """
    Get recommendations for a given content_id.
    Computes real cosine similarity scores against all other items.
    """
    engine = get_engine()
    result = engine.recommend(
        content_id=content_id,
        top_n=top_n,
        target_media=target_media,
        include_same_media=include_same_media,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/evaluate")
def get_evaluation():
    """
    Return evaluation statistics computed on the actual dataset.
    These are prototype-scale metrics, clearly labeled as such.
    """
    engine = get_engine()
    return engine.get_evaluation_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
