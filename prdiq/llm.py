"""Small LLM adapter (Anthropic Claude or Google Gemini) with bounded JSON retry behavior.

The provider follows the model name: models starting with "gemini" go to Google, everything else to Anthropic.
"""

import json
import re
from collections.abc import Callable
from typing import Any


DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
REQUEST_TIMEOUT_SECONDS = 30


class LLMError(RuntimeError):
    """Raised when the model cannot return a usable JSON response."""


def provider_for(model: str) -> str:
    return "gemini" if model.strip().lower().startswith("gemini") else "anthropic"


def provider_name(model: str) -> str:
    return "Google Gemini" if provider_for(model) == "gemini" else "Anthropic"


def _response_text(response: Any) -> str:
    for block in getattr(response, "content", ()):
        text = getattr(block, "text", None)
        if text:
            return text
    raise LLMError("The model response did not contain text.")


def _gemini_text(response: Any) -> str:
    candidates = getattr(response, "candidates", None) or []
    reason = str(getattr(candidates[0], "finish_reason", "") or "") if candidates else ""
    if not candidates or "SAFETY" in reason or "PROHIBITED" in reason:
        raise LLMError("The model declined the request.")
    if "MAX_TOKENS" in reason:
        raise LLMError("The model response was cut off.")
    text = getattr(response, "text", None)
    if not text:
        raise LLMError("The model response did not contain text.")
    return text


def _parse_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMError("The model returned invalid JSON.") from exc
    if not isinstance(value, dict):
        raise LLMError("The model response must be a JSON object.")
    return value


def _make_client(provider: str, api_key: str) -> Any:
    if provider == "gemini":
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise LLMError("Install the google-genai SDK to use Gemini.") from exc
        # The free tier often answers "model overloaded" (503) or "rate limited" (429); retry those briefly.
        retry = types.HttpRetryOptions(attempts=3, initial_delay=2.0, max_delay=10.0, http_status_codes=[429, 503])
        return genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_SECONDS * 1000, retry_options=retry),
        )
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise LLMError("Install the Anthropic SDK to use AI features.") from exc
    return Anthropic(api_key=api_key, timeout=float(REQUEST_TIMEOUT_SECONDS), max_retries=0)


def _request_text(provider: str, client: Any, model: str, system_prompt: str, prompt: str, max_tokens: int) -> str:
    if provider == "gemini":
        from google.genai import types

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                max_output_tokens=max_tokens,
                temperature=0,
                # low thinking keeps structured drafting/review inside the 30-second request limit
                thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
            ),
        )
        return _gemini_text(response)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    return _response_text(response)


def generate_json(
    *,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2400,
    client: Any = None,
    on_request: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Request JSON, retrying exactly once only when the JSON is malformed."""
    provider = provider_for(model)
    if client is None:
        client = _make_client(provider, api_key)

    last_error: LLMError | None = None
    for attempt in range(2):
        prompt = user_prompt
        if attempt:
            prompt += "\n\nYour previous response was not valid JSON. Return only one valid JSON object matching the requested shape."
        try:
            if on_request:
                on_request()
            return _parse_json(_request_text(provider, client, model, system_prompt, prompt, max_tokens))
        except LLMError as exc:
            last_error = exc
            if attempt == 1:
                break
    raise last_error or LLMError("The model response could not be parsed.")
