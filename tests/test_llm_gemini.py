from types import SimpleNamespace

import pytest

from prdiq.llm import DEFAULT_GEMINI_MODEL, LLMError, generate_json, provider_for, provider_name


class FakeGemini:
    """Stands in for google.genai.Client: returns the queued replies in order."""

    def __init__(self, *replies, finish="STOP"):
        self.replies = list(replies)
        self.finish = finish
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate)

    def _generate(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text=self.replies.pop(0), candidates=[SimpleNamespace(finish_reason=self.finish)])


def _ask(client, model=DEFAULT_GEMINI_MODEL):
    return generate_json(system_prompt="s", user_prompt="u", api_key="test", model=model, client=client)


@pytest.mark.parametrize("model, provider", [
    ("gemini-3.8-flash", "gemini"), ("Gemini-Pro", "gemini"), ("claude-sonnet-4-5", "anthropic"),
])
def test_provider_follows_model_name(model, provider):
    assert provider_for(model) == provider


def test_provider_display_name():
    assert provider_name("gemini-3.8-flash") == "Google Gemini"
    assert provider_name("claude-sonnet-4-5") == "Anthropic"


def test_gemini_returns_json_and_asks_for_json_mode():
    client = FakeGemini('{"findings": []}')
    assert _ask(client) == {"findings": []}
    config = client.calls[0]["config"]
    assert config.response_mime_type == "application/json" and config.system_instruction == "s"


def test_gemini_malformed_json_is_retried_once():
    client = FakeGemini("not json", '{"ok": true}')
    assert _ask(client) == {"ok": True}
    assert len(client.calls) == 2 and "not valid JSON" in client.calls[1]["contents"]


def test_gemini_safety_block_raises():
    with pytest.raises(LLMError, match="declined"):
        _ask(FakeGemini("", "", finish="SAFETY"))


def test_gemini_cut_off_reply_raises():
    with pytest.raises(LLMError, match="cut off"):
        _ask(FakeGemini('{"a":', '{"a":', finish="MAX_TOKENS"))


def test_every_request_is_counted():
    count = []
    generate_json(system_prompt="s", user_prompt="u", api_key="test", model=DEFAULT_GEMINI_MODEL,
                  client=FakeGemini("bad", '{"ok": 1}'), on_request=lambda: count.append(1))
    assert len(count) == 2  # the malformed-JSON retry counts toward the session limit too
