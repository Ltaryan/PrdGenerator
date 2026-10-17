# PRDIQ roadmap: next 3 months

| | |
|---|---|
| **Horizon** | November 2026 – January 2027 |
| **Format** | Now / Next / Later (commitment drops as the horizon grows) |
| **Inputs** | PRD section 3 (success measures), section 9 (what could go wrong), section 11 (improvements), evaluation results |

## Goal for the quarter

**Prove PRDIQ's findings are useful to real PMs before adding features**: measure whether findings are right and whether they change a PRD.

## How items were prioritised

| Evidence we have | What it points to |
|---|---|
| Rules find 7/7 planted flaws with 0 false alarms, but on **test PRDs written alongside the rules** | No proof yet on unseen PRDs → evaluation comes first |
| The LLM reviewer adds **4–6 quote-verified findings** per review, and the number varies between runs | Need to know if those extra findings are *useful*, not just verified |
| No usage or usefulness data is collected | Can't tell which features matter → add feedback and analytics |
| PRD section 3 lists success measures (task completion, usefulness, precision, recall) with **no baselines** | Instrument before setting targets |

---

## NOW: Month 1 (committed)

| Item | Why now | Success measure | Effort |
|---|---|---|---|
| **"Useful / not useful" on every finding** (with reason, consent, no PRD text stored) | The only way to measure usefulness and precision from real use; the experiment below depends on it | Feedback captured on ≥ 30% of findings shown | S |
| **Evaluation on unseen PRDs** (approved, de-identified, labelled by two people) | 7/7 on our own fixtures is a development check, not accuracy | Precision and recall reported per check | M |
| **Usage analytics** (privacy-safe events: draft created, review run, AI opt-in, export) | Baseline for task completion | Funnel: start → review → export visible | S |

## NEXT: Month 2 (planned, may change)

| Item | Why | Success measure | Effort |
|---|---|---|---|
| **Run the AI-review experiment** | Decide whether AI review should be recommended by default | Per [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) | M |
| **Editable AI drafts with a diff view** | Users must see what the AI changed versus their notes | Users accept or edit ≥ 1 section per draft | M |
| **Stronger sensitive-data tests** (addresses, account numbers, tokens) | Email/phone masking is basic; PRDs can contain more | New PII cases masked in tests | S |

## LATER: Month 3+ (direction, not commitment)

| Item | Why | Depends on |
|---|---|---|
| Team-configurable checklist (wording, severity, version recorded) | Different teams define "ready" differently | Usefulness data per check |
| Save drafts to a user-chosen location, with delete controls | Today nothing is stored, by design | Security review |
| Team workspaces, roles, audit logs | Only if pilots show demand | Evaluation + experiment results |

## Not doing this quarter

- **Jira or Notion sync:** integrations before proven usefulness would be wasted effort.
- **Fine-tuning a model:** the bottleneck is evaluation data, not the model.
- **Automatic PRD approval:** PRDIQ supports judgement, it doesn't replace it.

## What would change this plan

- Unseen-PRD evaluation shows low precision for some checks → fix or drop those checks before anything in NEXT.
- The experiment shows AI review adds no useful findings → keep AI optional and invest in the rules instead.
