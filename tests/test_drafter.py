from types import SimpleNamespace

from prdiq.drafter import Intake, SECTION_KEYS, draft_prd, skeleton_draft, ungrounded_numbers
from prdiq.llm import generate_json


def test_skeleton_preserves_inputs_and_marks_gaps_as_questions():
    draft = skeleton_draft(Intake(problem="Support agents retype answers from old tickets."))
    assert "Support agents retype answers from old tickets." in draft
    assert "OPEN QUESTION:" in draft
    assert "50%" not in draft


def test_number_grounding_detects_invented_digits():
    assert ungrounded_numbers("Improve success by 42%", "Improve support quality") == ("42",)
    assert not ungrounded_numbers("Reduce time by 20%", "Target is 20% faster")


class FakeMessages:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = 0

    def create(self, **kwargs):
        output = self.outputs[self.calls]
        self.calls += 1
        return SimpleNamespace(content=[SimpleNamespace(text=output)])


def test_json_parse_retries_once_after_broken_json():
    messages = FakeMessages(["not json", '{"ok": true}'])
    result = generate_json(
        system_prompt="Return JSON",
        user_prompt="Go",
        api_key="test",
        client=SimpleNamespace(messages=messages),
    )
    assert result == {"ok": True}
    assert messages.calls == 2


def test_invalid_or_ungrounded_ai_output_falls_back_to_skeleton():
    data = {key: "The feature supports users." for key in SECTION_KEYS}
    data["goal"] = "Improve resolution by 57%."
    payload = __import__("json").dumps(data)
    client = SimpleNamespace(messages=FakeMessages([payload]))
    result = draft_prd(Intake(problem="Support agents need better ticket answers."), use_ai=True, api_key="test", client=client)
    assert not result.used_ai
    assert "OPEN QUESTION:" in result.markdown
    assert any("number" in warning for warning in result.warnings)