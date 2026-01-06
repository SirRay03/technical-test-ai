from __future__ import annotations

import os
import httpx
from typing import Any, Dict

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(Exception):
    pass


def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise OpenRouterError("Missing OPENROUTER_API_KEY env var.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Optional, but recommended by OpenRouter docs for ranking/analytics
    http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "").strip()
    x_title = os.getenv("OPENROUTER_X_TITLE", "").strip()
    if http_referer:
        headers["HTTP-Referer"] = http_referer
    if x_title:
        headers["X-Title"] = x_title

    return headers


def summarize_cv_text(cv_text: str) -> Dict[str, Any]:
    """
    Calls OpenRouter Chat Completions API and requests a JSON-schema formatted response.
    """
    model = os.getenv("OPENROUTER_MODEL", "openai/o4-mini").strip()
    timeout_s = float(os.getenv("OPENROUTER_TIMEOUT_S", "30"))

    system_prompt = (
        "You are a recruiter assistant. Extract and summarize the candidate CV into JSON.\n"
        "Rules:\n"
        "- If a field is not present, set it to null (except work_experience_summary which must be a string).\n"
        "- Keep work_experience_summary to 3-6 sentences, focusing on roles, scope, impact, and seniority.\n"
        "- Do not invent facts.\n"
    )

    schema = {
        "name": "cv_summary",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "work_experience_summary": {"type": "string"},
            },
            "required": ["name", "location", "work_experience_summary"],
        },
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CV TEXT:\n\n{cv_text}"},
        ],
        # Structured outputs (works on compatible models)
        "response_format": {"type": "json_schema", "json_schema": schema},
        "temperature": 0.2,
    }

    url = f"{OPENROUTER_BASE_URL}/chat/completions"

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(url, headers=_get_headers(), json=payload)
    except Exception as e:
        raise OpenRouterError(f"Network error calling OpenRouter: {e}")

    if r.status_code >= 400:
        # OpenRouter returns error payloads; keep it simple for the assessment
        raise OpenRouterError(f"OpenRouter HTTP {r.status_code}: {r.text[:500]}")

    data = r.json()

    try:
        # OpenAI-like schema: choices[0].message.content should be JSON string under structured outputs
        content = data["choices"][0]["message"]["content"]
    except Exception:
        raise OpenRouterError(f"Unexpected OpenRouter response shape: {str(data)[:500]}")

    # content should already be JSON; parse defensively
    import json
    try:
        parsed = json.loads(content)
    except Exception:
        raise OpenRouterError(f"Model did not return valid JSON. Raw content: {content[:500]}")

    return parsed
