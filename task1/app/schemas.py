from pydantic import BaseModel, Field
from typing import Optional


class CVSummary(BaseModel):
    name: Optional[str] = Field(default=None, description="Candidate full name")
    location: Optional[str] = Field(default=None, description="City/region/country or current location")
    work_experience_summary: str = Field(
        ..., description="Concise summary of experience and impact (roles, domains, seniority, highlights)."
    )


class SummarizeResponse(BaseModel):
    extracted_chars: int
    summary: CVSummary


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
