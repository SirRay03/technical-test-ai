
# Tavily News Search API (Task 2)

## Overview
This service provides a simple, deployable API for retrieving **recent news articles** using the **Tavily Search API**.  
It allows clients to specify a **news area** (e.g., *AI developments*, *tech industry*) with an optional query, and returns a **normalized list of articles** suitable for downstream processing or display.

The API is implemented using **FastAPI** and is designed to be easy to run locally or in a containerized environment.

---

## Features
- Search news using Tavily’s real-time search capability
- Configurable search **area** and optional **query**
- Supports limiting results and time range
- Normalized output format:
  - `title`
  - `summary`
  - `source`
  - `date` (best-effort)
- Basic error handling for API and configuration failures

---

## API Endpoint

### `POST /v1/news/search`

#### Request Body
```json
{
  "area": "AI developments",
  "query": "model releases and regulation",
  "max_results": 5,
  "time_range": "week",
  "search_depth": "basic"
}
````

#### Parameters

| Field          | Type    | Required | Description                                              |
| -------------- | ------- | -------- | -------------------------------------------------------- |
| `area`         | string  | Yes      | Broad topic or industry area to search                   |
| `query`        | string  | No       | Additional search keywords                               |
| `max_results`  | integer | No       | Number of results to return (default: 5, max: 20)        |
| `time_range`   | string  | No       | Time window (`day`, `week`, `month`, `year`)             |
| `search_depth` | string  | No       | Search depth (`basic`, `advanced`, `fast`, `ultra-fast`) |

#### Response Example

```json
{
  "effective_query": "AI developments: model releases and regulation",
  "area": "AI developments",
  "results": [
    {
      "title": "In 2026, AI will move from hype to pragmatism",
      "url": "https://techcrunch.com/2026/01/02/in-2026-ai-will-move-from-hype-to-pragmatism/",
      "summary": "AI is expected to shift toward practical deployments, with advances in small language models, agentic systems, and world models...",
      "source": "techcrunch.com",
      "date": "Fri, 02 Jan 2026 14:43:00 GMT"
    }
  ]
}
```

---

## Setup

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
TAVILY_API_KEY=tvly_your_api_key_here
TAVILY_TIMEOUT_S=20
TAVILY_MAX_RESULTS_DEFAULT=5
TAVILY_TIME_RANGE_DEFAULT=week
TAVILY_SEARCH_DEPTH_DEFAULT=basic
```

> **Important:** Do not commit your `.env` file.

---

## Running the Service

### Local (Python)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker build -t tavily-news-api .
docker run --rm -p 8000:8000 --env-file .env tavily-news-api
```

---

## Testing the API

### Using `curl`

```bash
curl -X POST "http://localhost:8000/v1/news/search" \
  -H "Content-Type: application/json" \
  -d '{
    "area": "AI developments",
    "query": "model releases and regulation",
    "max_results": 5,
    "time_range": "week",
    "search_depth": "basic"
  }'
```

### PowerShell

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/v1/news/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "area":"AI developments",
    "query":"model releases and regulation",
    "max_results":5,
    "time_range":"week",
    "search_depth":"basic"
  }'
```

---

## Health Check

```bash
GET /health
```

Response:

```json
{ "status": "ok" }
```

---

## Assumptions & Limitations

* The service depends on a valid **Tavily API key**. If the key is missing or invalid, the API will return a `tavily_failed` error.
* The `date` field is **best-effort**. Tavily search results may not consistently provide publish timestamps across all sources.
* This service focuses on **news retrieval only** and does not perform additional ranking or summarization beyond Tavily’s returned content.

---

## Notes for Reviewers

* The integration uses Tavily’s `/search` endpoint with `topic="news"` to retrieve recent articles.
* Authentication is handled via `Authorization: Bearer <API_KEY>`.
* The codebase prioritizes clarity, explicit error handling, and easy deployment within the assessment time constraints.

```