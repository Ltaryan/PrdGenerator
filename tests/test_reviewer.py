import json
from types import SimpleNamespace

from prdiq.reviewer import retain_exact_source_quotes, review_with_ai


class FakeMessages:
    def __init__(self, payload):
        self.payload = payload

    def create(self, **kwargs):
        return SimpleNamespace(content=[SimpleNamespace(text=json.dumps(self.payload))])


def test_ai_review_drops_invented_quotes_and_unknown_checks():
    source = "The system falls back to manual review when the model is unavailable."
    client = SimpleNamespace(messages=FakeMessages({"findings": [
        {"check_id": "A2", "quote": "the model always fails safely", "explanation": "Missing fallback."},
        {"check_id": "NOPE", "quote": source, "explanation": "Unknown check."},
        {"check_id": "A2", "quote": source, "explanation": "Fallback behavior is underspecified."},
    ]}))
    findings = review_with_ai(source, api_key="test", client=client)
    assert len(findings) == 1
    assert findings[0].quote == source
    assert findings[0].quote in source


def test_ai_quote_changed_by_pii_redaction_is_not_presented_as_exact():
    source = "Support contact is alex@example.com for escalation."
    client = SimpleNamespace(messages=FakeMessages({"findings": [
        {"check_id": "A2", "quote": "Support contact is [REDACTED EMAIL] for escalation.", "explanation": "No fallback is specified."},
    ]}))
    findings = review_with_ai("Support contact is [REDACTED EMAIL] for escalation.", api_key="test", client=client)
    assert retain_exact_source_quotes(findings, source) == ()