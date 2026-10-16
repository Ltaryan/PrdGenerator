from prdiq.checklist import CHECKS
from prdiq.rules import review_prd
from prdiq.validation import MAX_INPUT_CHARS, find_note_conflicts, redact_sensitive, validate_text


def test_input_validation_blocks_empty_short_and_non_english_text():
    assert not validate_text("").valid
    assert not validate_text("The app is fast").valid
    assert any("English" in error for error in validate_text("".join(["La fonction est rapide pour tous les utilisateurs et simplifie notre travail quotidien."])).errors)


def test_input_is_truncated_and_sensitive_values_are_redacted():
    result = validate_text(("The product helps users with a useful workflow. " * 500) + "Contact jane@example.com or 212-555-0199.")
    assert len(result.sanitized_text) == MAX_INPUT_CHARS
    assert any("truncated" in warning for warning in result.warnings)
    assert "jane@example.com" not in result.sanitized_text
    assert "212-555-0199" not in result.sanitized_text
    assert "jane@example.com" not in redact_sensitive("Email jane@example.com")


def test_conflicts_between_goal_and_labeled_non_goal_are_flagged():
    conflicts = find_note_conflicts("Automate receipt categorization for bookkeepers", "Non-goal: automate receipt categorization")
    assert conflicts


def test_headings_alone_do_not_pass_checklist_items():
    headings = "\n".join(f"## {check.question}" for check in CHECKS)
    result = review_prd(headings)
    assert result.score == (0, 24)


def test_each_rule_finding_contains_a_verbatim_quote():
    prd = "## Problem\nUsers need help with a hard task.\n## Goals\nMake it easy."
    result = review_prd(prd)
    assert result.findings
    assert all(finding.quote in prd for finding in result.findings)


def test_heading_only_findings_still_quote_verbatim_source():
    prd = "## Problem\n## Users\n## Goal"
    result = review_prd(prd)
    assert result.findings
    assert all(finding.quote in prd for finding in result.findings)