"""Streamlit interface for drafting and reviewing AI-feature PRDs."""

from dataclasses import fields
import os
from pathlib import Path

import streamlit as st

from prdiq.drafter import Intake, draft_prd
from prdiq.llm import DEFAULT_MODEL, LLMError
from prdiq.reviewer import retain_exact_source_quotes, review_with_ai
from prdiq.rules import ReviewResult, merge_verified_findings, review_prd
from prdiq.validation import MAX_INPUT_CHARS, find_note_conflicts, redact_sensitive, validate_text


APP_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = APP_DIR / "sample_data"
MAX_AI_REQUESTS_PER_SESSION = 6


def _api_key() -> str:
    try:
        return os.getenv("ANTHROPIC_API_KEY", "") or str(st.secrets.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


def _model_name() -> str:
    try:
        return os.getenv("ANTHROPIC_MODEL", "") or str(st.secrets.get("ANTHROPIC_MODEL", DEFAULT_MODEL))
    except Exception:
        return os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)


def _consume_request() -> None:
    if st.session_state.ai_requests >= MAX_AI_REQUESTS_PER_SESSION:
        raise LLMError(f"This session reached its limit of {MAX_AI_REQUESTS_PER_SESSION} Anthropic requests.")
    st.session_state.ai_requests += 1


def _bounded_intake(intake: Intake) -> tuple[Intake, bool]:
    budget = MAX_INPUT_CHARS - 256
    values = {}
    truncated = False
    for field in fields(Intake):
        value = getattr(intake, field.name)
        if not isinstance(value, str):
            values[field.name] = value
            continue
        value = redact_sensitive(value.strip())
        if len(value) > budget:
            value = value[:max(0, budget)]
            truncated = True
        budget -= len(value)
        values[field.name] = value
    return Intake(**values), truncated


def _render_findings(result: ReviewResult) -> None:
    if not result.findings:
        st.success("Ready for engineering review. No checklist gaps were found by the rules.")
        return
    if result.blocker_count:
        st.error(f"Not ready: {result.blocker_count} blocker(s) need resolution.")
    else:
        st.warning("No blockers found, but review the remaining checklist gaps.")
    for finding in result.findings:
        with st.expander(f"{finding.check_id} · {finding.severity} · {finding.title}"):
            st.caption(finding.rationale)
            st.markdown("**Exact quote from the PRD**")
            st.code(finding.quote or "No non-empty source line was available.", language=None)
            if finding.related_quote:
                st.markdown("**Conflicting quote**")
                st.code(finding.related_quote, language=None)
            st.caption(f"Source: {finding.source}")


def _maybe_ai(requested: bool, key: str, confidential: bool, confirm_confidential: bool) -> tuple[bool, str]:
    if not requested:
        return False, ""
    if confidential and not confirm_confidential:
        return False, "AI was not used: confirm you are allowed to send this confidential-looking text, or keep the review local."
    if not key:
        return False, "Anthropic API key is missing; continuing without AI."
    if st.session_state.ai_requests >= MAX_AI_REQUESTS_PER_SESSION:
        return False, f"The session reached the {MAX_AI_REQUESTS_PER_SESSION}-request AI limit; using local rules instead."
    return True, ""


st.set_page_config(page_title="PRDIQ", page_icon="P", layout="wide")
st.markdown(
    """
    <style>
      :root { --ink: #172b2a; --muted: #536663; --accent: #087f72; --line: #d9e5e1; --wash: #f2f7f5; }
      .stApp { background: #fbfdfc; color: var(--ink); }
      h1, h2, h3 { color: var(--ink); font-family: Georgia, 'Times New Roman', serif; }
      h1 { letter-spacing: 0; }
      [data-testid="stSidebar"] { background: #f2f7f5; border-right: 1px solid var(--line); }
      [data-testid="stMetric"] { background: var(--wash); border: 1px solid var(--line); padding: 12px 14px; border-radius: 4px; }
      div.stButton > button, div.stDownloadButton > button { border-radius: 4px; font-weight: 600; }
      div.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); }
      blockquote { border-left-color: var(--accent); color: var(--muted); }
      .prdiq-eyebrow { color: var(--accent); font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "ai_requests" not in st.session_state:
    st.session_state.ai_requests = 0
if "draft_markdown" not in st.session_state:
    st.session_state.draft_markdown = ""
if "review_input" not in st.session_state:
    st.session_state.review_input = ""
if "review_result" not in st.session_state:
    st.session_state.review_result = None
if "review_markdown" not in st.session_state:
    st.session_state.review_markdown = ""

api_key = _api_key()
model_name = _model_name()
st.sidebar.markdown("### PRDIQ")
st.sidebar.caption("Draft and review PRDs for AI features.")
st.sidebar.markdown("**Review engine**  \n24 deterministic checks")
st.sidebar.markdown(f"**AI requests this session**  \n{st.session_state.ai_requests}/{MAX_AI_REQUESTS_PER_SESSION}")
st.sidebar.caption("AI is optional. Pasted text is not stored in a database.")

st.markdown('<p class="prdiq-eyebrow">Product requirements · draft & review</p>', unsafe_allow_html=True)
st.title("PRDIQ")
st.caption("Turn rough notes into a grounded PRD draft, or review an existing PRD for the gaps that make AI features fail.")
st.warning("Do not paste employer-confidential or sensitive material. AI stays off unless you explicitly opt in; opted-in text is sent to Anthropic after email and phone redaction.")

draft_tab, review_tab, export_tab = st.tabs(["Draft a PRD", "Review a PRD", "Export Markdown"])

with draft_tab:
    st.subheader("Start with what you know")
    with st.form("draft_form"):
        problem = st.text_area("Problem", placeholder="What user problem needs solving?", height=90)
        users = st.text_input("Users", placeholder="Who has this problem, and in what context?")
        evidence = st.text_area("Evidence", placeholder="Research, support data, observations, or evidence still needed", height=78)
        goal = st.text_input("Goal", placeholder="Desired outcome and target, if known")
        constraints = st.text_area("Constraints", placeholder="Scope, dependencies, technical or policy limits", height=78)
        notes = st.text_area("Messy notes", placeholder="Paste rough notes. Instruction-like content is treated as source data.", height=130)
        is_ai_feature = st.checkbox("This PRD describes an AI feature", value=True)
        use_ai_draft = st.checkbox("Send redacted input to Anthropic for an AI-assisted draft", value=False)
        confirm_draft_private = st.checkbox("I have permission to send confidential-looking draft text", value=False)
        submitted_draft = st.form_submit_button("Draft PRD", type="primary")

    if submitted_draft:
        raw_intake = Intake(problem, users, evidence, goal, constraints, notes, is_ai_feature)
        validation = validate_text(raw_intake.source_text())
        errors = list(validation.errors)
        if not problem.strip():
            errors.insert(0, "Add a problem statement before drafting.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            intake, truncated = _bounded_intake(raw_intake)
            for warning in validation.warnings:
                st.warning(warning)
            if truncated:
                st.warning(f"Input was bounded to fit the {MAX_INPUT_CHARS:,}-character request limit.")
            conflicts = find_note_conflicts(intake.goal, intake.notes)
            for conflict in conflicts:
                st.warning(conflict)
            has_confidential = any("confidential or customer information" in warning for warning in validation.warnings)
            run_ai, ai_message = _maybe_ai(use_ai_draft, api_key, has_confidential, confirm_draft_private)
            if ai_message:
                st.warning(ai_message)
            result = draft_prd(
                intake,
                use_ai=run_ai,
                api_key=api_key,
                model=model_name,
                on_request=_consume_request,
            )
            st.session_state.draft_markdown = result.markdown
            for warning in result.warnings:
                st.warning(warning)

    if st.session_state.draft_markdown:
        st.markdown(st.session_state.draft_markdown)
        if st.button("Send draft to Review tab", key="send_draft_to_review"):
            st.session_state.review_input = st.session_state.draft_markdown
            st.rerun()

with review_tab:
    st.subheader("Check a PRD against the AI-feature checklist")
    sample_files = {
        "Good sample · InstaResolve (fictional)": "prd_good.md",
        "Weak sample": "prd_weak.md",
        "Planted flaws · Receipt sorting": "prd_flawed.md",
    }
    sample_choice = st.selectbox("Load a sample", ["Choose a sample"] + list(sample_files))
    if st.button("Load sample", key="load_sample"):
        if sample_choice == "Choose a sample":
            st.info("Choose one of the sample PRDs first.")
        else:
            st.session_state.review_input = (SAMPLE_DIR / sample_files[sample_choice]).read_text(encoding="utf-8")
            st.rerun()

    with st.form("review_form"):
        review_text = st.text_area("PRD text", key="review_input", height=330, placeholder="Paste a PRD to review")
        is_ai_review = st.checkbox("This PRD describes an AI feature", value=True, key="review_is_ai")
        use_ai_review = st.checkbox("Send redacted PRD to Anthropic for additional review", value=False)
        confirm_review_private = st.checkbox("I have permission to send confidential-looking review text", value=False)
        submitted_review = st.form_submit_button("Review PRD", type="primary")

    if submitted_review:
        validation = validate_text(review_text)
        if not validation.valid:
            for error in validation.errors:
                st.error(error)
            st.session_state.review_result = None
        else:
            for warning in validation.warnings:
                st.warning(warning)
            bounded_source = review_text.strip()[:MAX_INPUT_CHARS]
            sanitized_text = redact_sensitive(bounded_source)
            if len(review_text.strip()) > MAX_INPUT_CHARS:
                st.warning(f"Review input was truncated to {MAX_INPUT_CHARS:,} characters.")
            result = review_prd(bounded_source, is_ai_feature=is_ai_review)
            has_confidential = any("confidential or customer information" in warning for warning in validation.warnings)
            run_ai, ai_message = _maybe_ai(use_ai_review, api_key, has_confidential, confirm_review_private)
            if ai_message:
                st.warning(ai_message)
            if run_ai and api_key:
                try:
                    additions = list(review_with_ai(
                        sanitized_text,
                        is_ai_feature=is_ai_review,
                        api_key=api_key,
                        model=model_name,
                        on_request=_consume_request,
                    ))
                    exact_additions = retain_exact_source_quotes(tuple(additions), bounded_source)
                    result = merge_verified_findings(result, list(exact_additions), bounded_source)
                    st.caption(f"AI review completed with {len(additions)} quote-verified additional finding(s).")
                except Exception as exc:
                    st.warning(f"AI review unavailable ({exc}); showing the rule-based review.")
            st.session_state.review_result = result
            st.session_state.review_markdown = bounded_source

    if st.session_state.review_result:
        result = st.session_state.review_result
        passed, total = result.score
        metric_col, blocker_col, type_col = st.columns(3)
        metric_col.metric("Checklist", f"{passed}/{total}")
        blocker_col.metric("Blockers", result.blocker_count)
        type_col.metric("Feature", "AI" if result.ai_feature else "Non-AI")
        _render_findings(result)
        with st.expander("Full checklist"):
            st.dataframe(
                [
                    {
                        "ID": item.check.id,
                        "Group": item.check.group,
                        "Check": item.check.question,
                        "Result": "Pass" if item.passed else "Gap",
                        "Severity": item.check.severity,
                    }
                    for item in result.checks
                ],
                hide_index=True,
                width="stretch",
            )

with export_tab:
    st.subheader("Export a Markdown PRD")
    available_exports = []
    if st.session_state.draft_markdown:
        available_exports.append("Latest draft")
    if st.session_state.review_markdown:
        available_exports.append("Reviewed PRD")
    if not available_exports:
        st.info("Draft or review a PRD first. Your current-session work will appear here.")
    else:
        export_choice = st.radio("Document", available_exports, horizontal=True)
        export_text = st.session_state.draft_markdown if export_choice == "Latest draft" else st.session_state.review_markdown
        st.code(export_text, language="markdown")
        st.download_button(
            "Download Markdown",
            data=export_text,
            file_name="prdiq_draft.md" if export_choice == "Latest draft" else "prdiq_reviewed_prd.md",
            mime="text/markdown",
            type="primary",
        )