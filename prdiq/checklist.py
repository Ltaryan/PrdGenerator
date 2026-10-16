"""Review criteria for product requirements documents."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    id: str
    group: str
    question: str
    rationale: str
    severity: str
    ai_only: bool = False
    terms: tuple[str, ...] = ()


CHECKS = (
    Check("P1", "Problem and users", "Is the user problem described?", "A clear problem prevents solution-first work.", "blocker", terms=("problem", "pain", "issue", "challenge")),
    Check("P2", "Problem and users", "Is the primary user named?", "A defined user makes requirements concrete.", "major", terms=("user", "customer", "operator", "person", "agent")),
    Check("P3", "Problem and users", "Is there evidence for the problem?", "Evidence distinguishes a real need from an assumption.", "major", terms=("interview", "research", "survey", "support ticket", "data", "evidence", "observed")),
    Check("P4", "Problem and users", "Is the current workflow or workaround explained?", "The current state provides a useful comparison.", "minor", terms=("currently", "today", "workaround", "manual", "existing workflow", "current workflow")),
    Check("G1", "Goals and scope", "Is an outcome stated with a measurable target?", "A target makes success falsifiable.", "blocker", terms=("target", "increase", "reduce", "improve", "within", "%", "by ")),
    Check("G2", "Goals and scope", "Are non-goals stated?", "Explicit exclusions prevent scope drift.", "major", terms=("non-goal", "out of scope", "will not", "won't", "not included")),
    Check("G3", "Goals and scope", "Is the proposed scope bounded?", "A bounded scope supports estimation and delivery.", "major", terms=("in scope", "scope", "phase 1", "v1", "version 1", "includes")),
    Check("G4", "Goals and scope", "Are constraints or dependencies called out?", "Known constraints surface delivery risks early.", "minor", terms=("constraint", "dependency", "depends on", "must use", "limited to", "requirement")),
    Check("R1", "Requirements", "Are key user flows or functional requirements described?", "Requirements tell design and engineering what to build.", "blocker", terms=("user can", "user flow", "workflow", "must allow", "the system", "when the user")),
    Check("R2", "Requirements", "Are acceptance criteria objectively testable?", "Testable criteria create a shared definition of done.", "blocker", terms=("acceptance criteria", "given ", "when ", "then ", "must be", "at least", "no more than")),
    Check("R3", "Requirements", "Are edge cases or error states covered?", "Failure and boundary behavior is part of the feature.", "major", terms=("error", "failure", "edge case", "unavailable", "timeout", "invalid", "empty state")),
    Check("R4", "Requirements", "Is an owner or decision-maker identified?", "A named owner keeps decisions and follow-up accountable.", "minor", terms=("owner", "decision maker", "product lead", "responsible", "team:")),
    Check("M1", "Metrics and evaluation", "Is the success metric defined with a target?", "A target enables an honest launch decision.", "blocker", terms=("success metric", "target", "baseline", "conversion", "latency", "accuracy", "completion rate")),
    Check("M2", "Metrics and evaluation", "Is the measurement baseline or source specified?", "A baseline makes change measurable and interpretable.", "major", terms=("baseline", "instrument", "analytics", "event", "dashboard", "source of truth")),
    Check("M3", "Metrics and evaluation", "Is AI quality evaluated on representative cases?", "Representative evaluation catches failures before users do.", "blocker", ai_only=True, terms=("evaluation", "eval", "test set", "test cases", "representative", "benchmark", "quality review")),
    Check("M4", "Metrics and evaluation", "Are guardrail metrics and thresholds defined?", "Guardrails expose regressions hidden by an average score.", "major", terms=("guardrail", "threshold", "false positive", "false negative", "escalation rate", "error rate")),
    Check("A1", "AI behavior and safeguards", "Is the AI behavior and its limits explained?", "Teams need to know what the model may and may not do.", "major", ai_only=True, terms=("model", "ai", "generated", "classification", "confidence", "limits", "uncertainty")),
    Check("A2", "AI behavior and safeguards", "Is there a fallback when the AI is unavailable or uncertain?", "A safe fallback keeps the product usable during failures.", "blocker", ai_only=True, terms=("fallback", "fail open", "fail closed", "manual mode", "unavailable", "low confidence")),
    Check("A3", "AI behavior and safeguards", "Is human review, handoff, or override defined?", "Human escalation contains consequential model mistakes.", "major", ai_only=True, terms=("human review", "human handoff", "handoff", "escalate", "override", "reviewer", "operator approves")),
    Check("A4", "AI behavior and safeguards", "Are model guardrails or prohibited outputs specified?", "Explicit boundaries reduce harmful or out-of-policy behavior.", "blocker", ai_only=True, terms=("guardrail", "prohibited", "must not", "refuse", "policy", "safety", "restricted")),
    Check("S1", "Risk, privacy, and rollout", "Are privacy and data handling requirements explicit?", "AI features can expose sensitive data in prompts, logs, or outputs.", "blocker", ai_only=True, terms=("privacy", "personal data", "pii", "retention", "consent", "redact", "data handling")),
    Check("S2", "Risk, privacy, and rollout", "Are material product or operational risks listed?", "Named risks can be mitigated and monitored.", "major", terms=("risk", "abuse", "misuse", "failure mode", "mitigation", "threat")),
    Check("S3", "Risk, privacy, and rollout", "Is the rollout plan defined?", "A staged rollout limits exposure while evidence is gathered.", "major", terms=("rollout", "pilot", "launch", "staged", "beta", "gradual")),
    Check("S4", "Risk, privacy, and rollout", "Are monitoring and rollback conditions defined?", "Teams need a trigger and action when the launch goes wrong.", "blocker", terms=("monitor", "alert", "rollback", "disable", "revert", "pause launch")),
)


def applicable_checks(is_ai_feature: bool) -> tuple[Check, ...]:
    """Return the full checklist or omit explicitly AI-only checks."""
    return tuple(check for check in CHECKS if is_ai_feature or not check.ai_only)