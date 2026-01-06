from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.schemas import NewsSearchRequest, NewsSearchResponse, NewsArticle, ErrorResponse
from app.tavily_client import tavily_news_search, normalize_articles, TavilyError

load_dotenv()

app = FastAPI(
    title="Tavily News Search API",
    version="1.0.0",
    description="Search news using Tavily with an area + optional query, returning normalized results.",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/v1/news/search",
    response_model=NewsSearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def news_search(req: NewsSearchRequest):
    # Construct effective query: area + optional query
    area = req.area.strip()
    if not area:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="invalid_request", detail="area must be non-empty").model_dump(),
        )

    effective_query = area if not req.query else f"{area}: {req.query.strip()}"

    # Allow env defaults if caller passes None (keeps endpoint easy to use)
    time_range = req.time_range or os.getenv("TAVILY_TIME_RANGE_DEFAULT", "week")
    search_depth = req.search_depth or os.getenv("TAVILY_SEARCH_DEPTH_DEFAULT", "basic")

    try:
        raw = tavily_news_search(
            effective_query=effective_query,
            max_results=req.max_results,
            time_range=time_range,
            search_depth=search_depth,
        )
        normalized = normalize_articles(raw)
        articles = [NewsArticle(**a) for a in normalized]
    except TavilyError as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="tavily_failed", detail=str(e)).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="unexpected_error", detail=str(e)).model_dump(),
        )

    return NewsSearchResponse(effective_query=effective_query, area=area, results=articles)
