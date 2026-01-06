from __future__ import annotations

import io
import pdfplumber


class PDFTextExtractionError(Exception):
    pass


def extract_text_from_pdf_bytes(pdf_bytes: bytes, max_chars: int = 20_000) -> str:
    """
    Extracts text from a PDF using pdfplumber and returns a capped string.
    max_chars: caps output to reduce token usage & latency.
    """
    if not pdf_bytes or len(pdf_bytes) < 5:
        raise PDFTextExtractionError("Empty or invalid PDF file.")

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            parts = []
            for page in pdf.pages:
                txt = page.extract_text() or ""
                if txt.strip():
                    parts.append(txt)
            full = "\n\n".join(parts).strip()
    except Exception as e:
        raise PDFTextExtractionError(f"Failed to read PDF: {e}")

    if not full:
        raise PDFTextExtractionError("No extractable text found (PDF may be scanned/image-only).")

    # Cap size for LLM
    if len(full) > max_chars:
        full = full[:max_chars] + "\n\n[TRUNCATED]"
    return full
