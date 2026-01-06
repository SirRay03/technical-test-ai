# Task 1 — PDF CV Summarization API

## Overview

This service exposes a REST API that accepts a **PDF CV / resume**, extracts its text content, and generates a **structured summary** using an LLM via **OpenRouter**.

The response includes:

* Candidate name
* Location
* Concise work experience summary

The service is designed to be deployable, configurable via environment variables, and robust to common failure modes (invalid PDFs, external API errors).

---

## Tech Stack

* **Python 3.11**
* **FastAPI** — API framework
* **pdfplumber** — PDF text extraction
* **OpenRouter API** — LLM integration
* **Docker** — containerization (optional)

---

## API Specification

### Endpoint

```
POST /v1/cv/summarize
```

### Request

* `multipart/form-data`
* Field: `file` (PDF file)

### Response (200 OK)

```json
{
  "extracted_chars": 12456,
  "summary": {
    "name": "John Doe",
    "location": "Jakarta, Indonesia",
    "work_experience_summary": "Software engineer with 5+ years of experience..."
  }
}
```

### Error Responses

| Status | Error Code              | Description               |
| ------ | ----------------------- | ------------------------- |
| 400    | `invalid_file`          | Non-PDF or malformed file |
| 400    | `pdf_extraction_failed` | No extractable text       |
| 500    | `llm_failed`            | OpenRouter error          |
| 500    | `unexpected_error`      | Unhandled server error    |

---

## Local Setup

### 1. Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/o4-mini
OPENROUTER_TIMEOUT_S=30
PDF_MAX_CHARS=20000
```

> `PDF_MAX_CHARS` limits the extracted text size to control latency and token usage.

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```
GET http://localhost:8000/health
```

---

## Testing the API

### Using curl (Git Bash / WSL)

```bash
curl -X POST http://localhost:8000/v1/cv/summarize \
  -H "accept: application/json" \
  -F "file=@path/to/cv.pdf"
```

### Using PowerShell

```powershell
Invoke-WebRequest `
  -Uri "http://localhost:8000/v1/cv/summarize" `
  -Method POST `
  -Headers @{ Accept = "application/json" } `
  -Form @{ file = Get-Item "cv.pdf" }
```

---

## Docker (Optional)

```bash
docker build -t cv-summarizer .
docker run --rm -p 8000:8000 --env-file .env cv-summarizer
```

---

## Assumptions & Limitations

### PDF Handling

* Only **text-based PDFs** are supported.
* Scanned or image-only PDFs will fail with `pdf_extraction_failed`.
* OCR is intentionally omitted to keep scope and runtime minimal.

### LLM Dependency (OpenRouter)

* The summarization step depends on an active **OpenRouter account with available credits**.
* If the API key has **no credits**, OpenRouter returns:

  ```
  HTTP 402 – Insufficient credits
  ```
* In this case, the service responds with:

  ```json
  {
    "error": "llm_failed",
    "detail": "OpenRouter HTTP 402: Insufficient credits"
  }
  ```
* The PDF ingestion and extraction pipeline still executes successfully.

### Model Behavior

* The LLM is instructed **not to hallucinate** and to return `null` for missing fields.
* Output is constrained using structured JSON schema where supported by the model.

---

## Design Notes

* Configuration is fully environment-driven for easy deployment.
* Text extraction is capped to avoid excessive token usage.
* External API failures are explicitly handled and surfaced clearly to clients.

---

## Status

Task 1 implementation complete and ready for evaluation.
