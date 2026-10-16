"""Input limits, language checks, and sensitive-text handling."""

from dataclasses import dataclass
import re


MAX_INPUT_CHARS = 20_000
MIN_WORDS = 8
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_ENGLISH_MARKERS = {
    "a", "and", "are", "as", "at", "by", "can", "for", "from", "has",
    "in", "is", "it", "of", "on", "or", "our", "that", "the", "this",
    "to", "we", "will", "with", "you",
}
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d().\- ]{7,}\d)(?!\w)")
_CONFIDENTIAL_RE = re.compile(r"\b(confidential|proprietary|internal only|do not share|customer records?)\b", re.I)
_INSTRUCTION_RE = re.compile(r"\b(ignore (all|any|previous|prior)|disregard (all|any|previous|prior)|reveal your system prompt)\b", re.I)


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    sanitized_text: str

    @property
    def valid(self) -> bool:
        return not self.errors


def validate_text(text: str, *, min_words: int = MIN_WORDS) -> ValidationResult:
    """Validate pasted text and return its bounded, redacted form."""
    errors: list[str] = []
    warnings: list[str] = []
    value = text.strip()
    if not value:
        return ValidationResult(("Paste a PRD or add notes before running this action.",), (), "")

    if len(value) > MAX_INPUT_CHARS:
        value = value[:MAX_INPUT_CHARS]
        warnings.append(f"Input was truncated to {MAX_INPUT_CHARS:,} characters.")

    words = _WORD_RE.findall(value)
    if len(words) < min_words:
        errors.append(f"Add more detail: at least {min_words} words are needed; found {len(words)}.")
    elif len(words) >= 12:
        markers = {word.lower() for word in words} & _ENGLISH_MARKERS
        latin_letters = sum(character.isascii() and character.isalpha() for character in value)
        all_letters = sum(character.isalpha() for character in value)
        if all_letters and latin_letters / all_letters < 0.65 or len(markers) < 2:
            errors.append("This text may not be in English. PRDIQ currently reviews English PRDs only.")

    if _CONFIDENTIAL_RE.search(value):
        warnings.append("This may contain confidential or customer information. Do not send employer-confidential text to an AI service.")
    if _INSTRUCTION_RE.search(value):
        warnings.append("Instruction-like text detected. It will be treated as source content, not as directions to PRDIQ.")

    before = value
    value = redact_sensitive(value)
    if value != before:
        warnings.append("Email addresses and phone numbers were masked before processing.")

    return ValidationResult(tuple(errors), tuple(dict.fromkeys(warnings)), value)


def redact_sensitive(text: str) -> str:
    """Mask common direct identifiers before text leaves the local app."""
    return _PHONE_RE.sub("[REDACTED PHONE]", _EMAIL_RE.sub("[REDACTED EMAIL]", text))


def find_conflicts(goal: str, non_goals: str) -> tuple[str, ...]:
    """Flag direct lexical overlap between a stated goal and non-goals."""
    goal_terms = {term for term in _WORD_RE.findall(goal.lower()) if len(term) > 3}
    non_goal_terms = {term for term in _WORD_RE.findall(non_goals.lower()) if len(term) > 3}
    overlap = goal_terms & non_goal_terms
    if len(overlap) >= 2:
        shared = ", ".join(sorted(overlap))
        return (f"Possible goal/non-goal conflict: both fields mention {shared}. Review this manually.",)
    return ()


def find_note_conflicts(goal: str, notes: str) -> tuple[str, ...]:
    non_goal_lines = [
        match.group(1)
        for line in notes.splitlines()
        if (match := re.match(r"\s*(?:non[- ]goals?|out of scope)\s*:\s*(.+)", line, re.I))
    ]
    return find_conflicts(goal, "\n".join(non_goal_lines)) if non_goal_lines else ()