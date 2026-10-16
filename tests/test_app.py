from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_dark_theme_toggle_switches_palette():
    app = AppTest.from_file(str(APP_PATH)).run()
    toggle = next(item for item in app.toggle if item.label == "Dark theme")
    toggle.set_value(True).run()

    assert not app.exception
    assert any("#101817" in item.value for item in app.markdown)


def test_review_without_api_key_shows_rule_fallback(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    app = AppTest.from_file(str(APP_PATH)).run()
    app.text_area(key="review_input").set_value(
        "The user requests an AI review of this product requirements document using the current notes."
    )
    next(
        checkbox
        for checkbox in app.checkbox
        if checkbox.label == "Send redacted PRD to Anthropic for additional review"
    ).set_value(True)
    next(button for button in app.button if button.label == "Review PRD").click().run()

    assert not app.exception
    assert any("API key is missing; continuing without AI" in item.value for item in app.warning)
    assert app.metric[0].value != "0/0"