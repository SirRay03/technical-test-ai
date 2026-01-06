from __future__ import annotations

import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.pdf_utils import extract_text_from_pdf_bytes, PDFTextExtractionError
from app.openrouter_client import summarize_cv_text, OpenRouterError
from app.schemas import SummarizeResponse, ErrorResponse, CVSummary

load_dotenv()

app = FastAPI(
    title="CV Summarizer API",
    version="1.0.0",
    description="Upload a PDF CV/resume, extract text, summarize via OpenRouter.",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/v1/cv/summarize",
    response_model=SummarizeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def summarize_cv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="invalid_file", detail="Only .pdf files are accepted.").model_dump(),
        )

    pdf_bytes = await file.read()
    max_chars = int(os.getenv("PDF_MAX_CHARS", "20000"))

    try:
        text = extract_text_from_pdf_bytes(pdf_bytes, max_chars=max_chars)
    except PDFTextExtractionError as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="pdf_extraction_failed", detail=str(e)).model_dump(),
        )

    try:
        summary_dict = summarize_cv_text(text)
        summary = CVSummary(**summary_dict)
    except OpenRouterError as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="llm_failed", detail=str(e)).model_dump(),
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="unexpected_error", detail=str(e)).model_dump(),
        )

    return SummarizeResponse(extracted_chars=len(text), summary=summary)
