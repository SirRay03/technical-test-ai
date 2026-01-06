# CV Summarizer API (Task 1)

## What it does
- Accepts a PDF CV/resume upload
- Extracts text from the PDF
- Calls OpenRouter LLM to return structured JSON:
  - name
  - location
  - work_experience_summary

## Requirements
- Python 3.11+
- An OpenRouter API key

## Setup (local)
```bash
cp .env.example .env
# edit .env and set OPENROUTER_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
