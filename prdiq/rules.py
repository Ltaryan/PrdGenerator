"""Deterministic PRD checklist reviewer."""

from dataclasses import dataclass
import re

from prdiq.checklist import Check, applicable_checks


_HEADING_RE = re.compile(r"^\s{0,3}(?:#{1,6}\s+|[A-Z][A-Z0-9 /&'()-]{2,}:\s*$)")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|ms|seconds?|minutes?|hours?|days?|users?|requests?)?\b", re.I)


@dataclass(frozen=True)
class Finding:
    check_id: str
    group: str
    severity: str
    title: str
    rationale: str
    quote: str
    source: str = "Rules"
    related_quote: str = ""


@dataclass(frozen=True)
class CheckResult:
    check: Check
    passed: bool
    finding: Finding | None


@dataclass(frozen=True)
class ReviewResult:
    checks: tuple[CheckResult, ...]
    findings: tuple[Finding, ...]
    ai_feature: bool

    @property
    def score(self) -> tuple[int, int]:
        return sum(result.passed for result in self.checks), len(self.checks)

    @property
    def blocker_count(self) -> int:
        return sum(finding.severity == "blocker" for finding in self.findings)


def _content_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
        and not _HEADING_RE.match(line)
        and not re.match(r"^\s*(?:OPEN QUESTION|ASSUMPTION)\s*:", line, re.I)
    ]


def _has_testable_criteria(body: str) -> bool:
    for line in body.splitlines():
        gherkin = re.search(r"\bgiven\b.*\bwhen\b.*\bthen\b", line, re.I)
        measurable_action = (
            re.search(r"\b(must|shall|returns?|shows?|allows?)\b", line, re.I)
            and _NUMBER_RE.search(line)
        )
        if gherkin or measurable_action:
            return True
    return False


def _has_target(body: str) -> bool:
    return bool(_NUMBER_RE.search(body) and re.search(r"\b(target|increase|reduce|improve|within|at least|no more than|below|above|by)\b", body, re.I))


def _is_satisfied(check: Check, body: str) -> bool:
    lowered = body.lower()
    if check.id in {"G1", "M1"}:
        return _has_target(body)
    if check.id == "R2":
        return _has_testable_criteria(body)
    if check.id == "M2":
        return any(term in lowered for term in check.terms) and bool(re.search(r"\b(baseline|analytics|instrument|event|dashboard|source of truth)\b", lowered))
    return any(term in lowered for term in check.terms)


def _quote_for(check: Check, lines: list[str]) -> str:
    if not lines:
        return ""
    for line in lines:
        if any(term in line.lower() for term in check.terms):
            return line
    return lines[0]


def review_prd(text: str, *, is_ai_feature: bool = True) -> ReviewResult:
    """Score applicable checks using body text; headings never count as evidence."""
    lines = _content_lines(text)
    quote_lines = [line.strip() for line in text.splitlines() if line.strip()]
    body = "\n".join(lines)
    check_results: list[CheckResult] = []
    findings: list[Finding] = []

    for check in applicable_checks(is_ai_feature):
        passed = _is_satisfied(check, body)
        finding = None
        if not passed:
            finding = Finding(
                check_id=check.id,
                group=check.group,
                severity=check.severity,
                title=check.question,
                rationale=check.rationale,
                quote=_quote_for(check, lines or quote_lines),
            )
            findings.append(finding)
        check_results.append(CheckResult(check=check, passed=passed, finding=finding))

    return ReviewResult(tuple(check_results), tuple(findings), is_ai_feature)


def merge_verified_findings(review: ReviewResult, additions: list[Finding], source_text: str) -> ReviewResult:
    """Merge AI findings only when their check exists and quote is exact."""
    known_ids = {result.check.id for result in review.checks}
    accepted: list[Finding] = []
    for finding in additions:
        if finding.check_id not in known_ids or not finding.quote or finding.quote not in source_text:
            continue
        if any(existing.check_id == finding.check_id for existing in review.findings + tuple(accepted)):
            continue
        accepted.append(finding)

    if not accepted:
        return review

    accepted_ids = {finding.check_id for finding in accepted}
    updated_checks = tuple(
        CheckResult(result.check, False, next(f for f in accepted if f.check_id == result.check.id))
        if result.check.id in accepted_ids and result.passed
        else result
        for result in review.checks
    )
    return ReviewResult(updated_checks, review.findings + tuple(accepted), review.ai_feature)