from __future__ import annotations

import os
import httpx
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class TavilyError(Exception):
    pass


def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise TavilyError("Missing TAVILY_API_KEY env var.")

    return {
        "Authorization": f"Bearer {api_key}",  # Tavily docs specify Bearer auth
        "Content-Type": "application/json",
    }


def _domain_from_url(url: str) -> Optional[str]:
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "") if netloc else None
    except Exception:
        return None


def tavily_news_search(
    effective_query: str,
    max_results: int,
    time_range: str,
    search_depth: str,
) -> List[Dict[str, Any]]:
    """
    Calls Tavily Search API using topic='news' and returns raw Tavily 'results' list.
    """
    timeout_s = float(os.getenv("TAVILY_TIMEOUT_S", "20"))

    payload = {
        "query": effective_query,
        "topic": "news",                 # documented as 'news' for real-time updates
        "max_results": max_results,      # 0..20
        "time_range": time_range,        # day/week/month/year (also d/w/m/y)
        "search_depth": search_depth,    # advanced/basic/fast/ultra-fast
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
        "include_favicon": False,
    }

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(TAVILY_SEARCH_URL, headers=_get_headers(), json=payload)
    except Exception as e:
        raise TavilyError(f"Network error calling Tavily: {e}")

    if r.status_code >= 400:
        raise TavilyError(f"Tavily HTTP {r.status_code}: {r.text[:500]}")

    data = r.json()
    results = data.get("results", [])
    if not isinstance(results, list):
        raise TavilyError("Unexpected Tavily response: results is not a list.")
    return results


def normalize_articles(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes Tavily results to the assessment format:
    title, summary, source, date.
    Note: Tavily 'results' commonly include title/url/content; publish date may be absent.
    """
    articles: List[Dict[str, Any]] = []
    for item in results:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        summary = (item.get("content") or "").strip()

        if not title or not url:
            continue

        source = _domain_from_url(url)
        # Date fields may vary / be absent; keep optional.
        date = item.get("published_date") or item.get("date") or item.get("published")  # best-effort

        articles.append(
            {
                "title": title,
                "url": url,
                "summary": summary,
                "source": source,
                "date": date,
            }
        )
    return articles
