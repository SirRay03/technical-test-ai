from pydantic import BaseModel, Field
from typing import List, Optional, Literal


TimeRange = Literal["day", "week", "month", "year", "d", "w", "m", "y"]
SearchDepth = Literal["advanced", "basic", "fast", "ultra-fast"]


class NewsSearchRequest(BaseModel):
    area: str = Field(..., description="News area/category, e.g., 'AI developments', 'tech industry'.")
    query: Optional[str] = Field(default=None, description="Optional specific query inside the area.")
    max_results: int = Field(default=5, ge=1, le=20)
    time_range: Optional[TimeRange] = Field(default="week")
    search_depth: SearchDepth = Field(default="basic")


class NewsArticle(BaseModel):
    title: str
    url: str
    summary: str
    source: Optional[str] = None
    date: Optional[str] = None  # Tavily may not always provide publish date; kept optional.


class NewsSearchResponse(BaseModel):
    effective_query: str
    area: str
    results: List[NewsArticle]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
