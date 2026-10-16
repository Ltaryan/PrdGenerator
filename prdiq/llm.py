"""Small Anthropic adapter with bounded JSON retry behavior."""

import json
import re
from collections.abc import Callable
from typing import Any


DEFAULT_MODEL = "claude-sonnet-4-5"


class LLMError(RuntimeError):
    """Raised when the model cannot return a usable JSON response."""


def _response_text(response: Any) -> str:
    for block in getattr(response, "content", ()):
        text = getattr(block, "text", None)
        if text:
            return text
    raise LLMError("The model response did not contain text.")


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
    if client is None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise LLMError("Install the Anthropic SDK to use AI features.") from exc
        client = Anthropic(api_key=api_key, timeout=30.0, max_retries=0)

    last_error: LLMError | None = None
    for attempt in range(2):
        prompt = user_prompt
        if attempt:
            prompt += "\n\nYour previous response was not valid JSON. Return only one valid JSON object matching the requested shape."
        try:
            if on_request:
                on_request()
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return _parse_json(_response_text(response))
        except LLMError as exc:
            last_error = exc
            if attempt == 1:
                break
    raise last_error or LLMError("The model response could not be parsed.")