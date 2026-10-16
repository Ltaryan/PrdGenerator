# PRDIQ — Product Requirements and Project Guide

This document is both the product requirements document (PRD) for PRDIQ and a plain-language guide to running, using, evaluating, and improving it. It describes the current code, not a claim that every suggested future improvement is already built.

## 1. The project in one minute

**PRDIQ** is a small web app that helps a product team draft and check product requirements documents (PRDs), especially PRDs for AI features.

A PRD is a shared plan for a product change. It explains the user problem, who has it, what the product should do, how success will be measured, and how the team will handle failures and risks.

PRDIQ has two main jobs:

1. **Draft:** Turn notes into a structured Markdown PRD. Missing facts stay visible as `OPEN QUESTION`s instead of being quietly made up. An optional AI draft can organize the notes.
2. **Review:** Check an existing PRD against a checklist. Local rules run without AI. Optional AI review can add findings, but its quotes must match the source text.

It is a checklist and drafting assistant, not an automatic product manager, a source of user research, or a guarantee that a PRD is correct.

## 2. Why we made it

PRDs often look complete while leaving out important decisions: who the user is, what counts as success, what happens when an AI model fails, or how a team will protect data. Those gaps can lead to wasted engineering work, unsafe behavior, or a launch whose results cannot be judged.

PRDIQ makes common gaps easier to notice early and gives a team a repeatable starting structure. It is especially useful when:

- A product idea begins as rough notes.
- A team needs to check whether an AI feature has evaluation, privacy, human-review, and fallback plans.
- A reviewer wants concrete checklist gaps with quotes, rather than only a vague score.
- Someone needs a Markdown draft that can be edited or shared elsewhere.

**Product hypothesis:** If teams see missing decisions sooner, they can write clearer requirements and reduce avoidable rework. This is a hypothesis to validate with users; the sample files in this repository do not prove the product has achieved that outcome.

## 3. Product requirements

### Users and problem

- **Primary intended users:** Product managers and product teams who write or review PRDs, including teams planning AI features.
- **User need:** “Help me turn incomplete notes into a useful PRD, and show me important missing decisions before my team builds.”
- **Evidence status:** The repository contains illustrative sample PRDs and developer-authored test fixtures. It does not contain documented customer interviews, a validated user-research study, or measured adoption results. Those should be collected before making claims about demand or impact.

### Goals

- Make PRD drafting and checklist review available in a browser.
- Keep missing information visible instead of inventing facts.
- Make the local checklist repeatable and explainable.
- Let people use the core workflow without an AI key.
- Make it easy to export Markdown.
- Give AI use an explicit opt-in and apply basic input safeguards.

### Non-goals in the current version

- Replacing product, legal, security, research, or engineering judgment.
- Proving that a feature is safe or that an AI system is accurate.
- Training or fine-tuning an AI model.
- Keeping a permanent history of user documents in a product database.
- Accounts, team collaboration, permissions, comments, Jira integration, or Notion sync.
- Automatically publishing a PRD or launching a product.

### Requirements and current behavior

| ID | Requirement | Current implementation / acceptance check |
|---|---|---|
| F1 | A user can draft from notes. | The Draft tab asks for problem, users, evidence, goal, constraints, and notes. A problem statement is required. |
| F2 | Missing facts are not presented as known facts. | The offline draft uses `OPEN QUESTION`; AI instructions require questions for missing facts and label inferences as assumptions. |
| F3 | A user can check a PRD. | The Review tab reports a score, blockers, findings, source quotes, and a full checklist. |
| F4 | Core review works without AI. | The deterministic rules run locally; a missing key or AI failure leaves the rules-based result available. |
| F5 | AI use requires an explicit choice. | Drafting and review have separate opt-in checkboxes. Confidential-looking text also requires a confirmation checkbox before the AI option is used. |
| F6 | A user can export Markdown. | The Export Markdown tab offers the latest draft or reviewed PRD for download. |
| F7 | The interface works in light and dark themes. | A sidebar toggle changes the page palette. |
| F8 | A PRD can be marked as non-AI. | AI-only checklist items are omitted when the non-AI option is selected. |

### Success measures to establish

These are recommended product measures, not metrics currently reported by the app:

- **Task completion:** share of users who successfully draft or review and export a PRD.
- **Time saved:** time to produce a usable first draft, compared with the team’s prior workflow.
- **Usefulness:** share of findings users say helped them make a decision.
- **Precision:** share of findings that human reviewers agree are real gaps.
- **Recall:** share of known, important gaps that the reviewer catches.
- **Safety/usability guardrails:** accidental sensitive-data submissions, incorrect or misleading findings, AI errors, and users abandoning because a result is confusing.

Set a baseline and target only after collecting permissioned, representative observations. Do not treat the checklist score as product success or AI accuracy.

## 4. What the app checks

The full checklist has **24 checks** across six groups. Six checks are AI-only, so selecting a non-AI feature leaves 18 applicable checks.

| Group | Examples of questions |
|---|---|
| Problem and users | Is the problem explained? Is a primary user named? Is there evidence and a description of the current workaround? |
| Goals and scope | Is there a measurable target? Are non-goals, scope, constraints, and dependencies stated? |
| Requirements | Are user flows, testable acceptance criteria, edge cases, and an owner described? |
| Metrics and evaluation | Are success measures, baselines, representative AI evaluations, and guardrail thresholds described? |
| AI behavior and safeguards | Are model limits, failure fallback, human review, and prohibited behavior described? |
| Risk, privacy, and rollout | Are data handling, risks, rollout, monitoring, and rollback covered? |

Each check has a severity: **blocker**, **major**, or **minor**. A blocker means the checklist considers the gap especially important; it is not a legal or launch approval.

The rule reviewer looks for configured words and patterns in PRD body text. Headings and lines marked `OPEN QUESTION` or `ASSUMPTION` are excluded as evidence. Findings include a quote from the source when a non-empty line is available. These are useful safeguards for explainability, but keyword matching is not the same as understanding meaning.

Optional AI review checks the PRD against the same checklist. An AI addition is accepted only for a known check, with an exact quote present in the original PRD, and only if it does not duplicate an existing finding. It supplements rather than replaces the rule review.

## 5. How to use the web app

### Start it locally on Windows

From the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
streamlit run app.py
```

Streamlit prints a local address, usually `http://localhost:8501`. Open it in a browser. If the virtual environment already exists, activate it and run `streamlit run app.py`. The README also documents activation on macOS/Linux.

### Draft a PRD

1. Open **Draft a PRD**.
2. Fill in the problem. Add users, evidence, goal, constraints, and rough notes when known.
3. Leave AI off to create a local skeleton, or explicitly check the AI draft option.
4. Only check the confidential-text confirmation if you have permission to send the content. Do not use it to send information you are not authorized to share.
5. Select **Draft PRD** and read all warnings and open questions.
6. Use **Send draft to Review tab** if you want to check the draft next.

**Example:** If your note says “Support agents search many old tickets,” PRDIQ can keep that statement in the problem section and ask who the users are or what result should improve. It should not invent a target such as “30% faster.”

### Review a PRD

1. Open **Review a PRD**.
2. Optionally load the fictional good sample, weak sample, or planted-flaws sample.
3. Paste or edit the PRD and select whether it describes an AI feature.
4. Leave AI off for a local checklist review, or explicitly opt into an additional AI review (Anthropic or Gemini, whichever key is set).
5. Select **Review PRD**.
6. Read the score, blockers, each finding’s quote and rationale, and the full checklist. Verify findings yourself; a passed check is not proof of quality.

### Export

Open **Export Markdown**, choose the latest draft or reviewed PRD, then select **Download Markdown**. The exported file is ordinary Markdown and can be edited in a text editor.

### Optional AI setup (Anthropic or Gemini)

AI draft/review needs one API key: `ANTHROPIC_API_KEY` (Claude, paid) or `GEMINI_API_KEY` (Google Gemini, free tier from aistudio.google.com/apikey). Put it in a local `.env` file (copy `.env.example`; `.env` is git-ignored), the environment, or Streamlit secrets. Optionally set `ANTHROPIC_MODEL` (default `claude-sonnet-4-5`) or `GEMINI_MODEL` (default `gemini-3.6-flash`). If both keys are set, Anthropic is used unless `AI_PROVIDER=gemini`; the app shows the active provider's name wherever text may be sent. `.env.example` is a placeholder—never put a real key in a committed file. Follow your organization’s approved secret-management process for hosted deployment.

AI is opt-in for each action. The app warns against confidential material, masks common email addresses and phone numbers before AI requests, limits each Streamlit session to six counted AI requests, and uses a 30-second client timeout. The configured request limit is six; a malformed-JSON retry also counts as a request.

## 6. What is used in the project

| Component | What it does |
|---|---|
| Python | Implements the app and review/drafting logic. |
| Streamlit | Builds the browser interface and holds current session UI state. |
| Anthropic Python SDK | Makes optional Claude calls when the user opts in and an Anthropic key is configured. |
| Google GenAI SDK | Makes optional Gemini calls (free tier available) when the user opts in and a Gemini key is configured. |
| Model settings | Claude defaults to `claude-sonnet-4-5`, Gemini to `gemini-3.6-flash`; both can be changed with configuration. No model is needed for local rules or export. |
| python-dotenv | Reads API keys from a local, git-ignored `.env` file. |
| pytest | Runs automated tests for the app, checklist, drafting, reviewing, and validation. |
| Markdown | Stores sample PRDs and is the export format. |
| Git | Tracks project source and documentation. |

The main implementation is in [app.py](./app.py). Reusable drafting, checklist, review, model adapter, and input validation logic live in [prdiq/](./prdiq). Sample documents are in [sample_data/](./sample_data), and tests are in [tests/](./tests).

## 7. Sample data: what it is and how to use it

### What is in the repository

- `sample_data/prd_good.md` is an explicitly **fictional** example about support-ticket suggestions. It is written to pass the current 24 checks. It is not customer research or proof of app accuracy.
- `sample_data/prd_weak.md` is a short example with vague claims, useful for trying the interface.
- `sample_data/prd_flawed.md` is a fictional receipt-sorting PRD with known omissions.
- `sample_data/planted_flaws.json` labels seven expected gaps in that planted-flaws document.
- `prdiq/evaluation.py` compares the rule results with those labels. The tests expect all seven planted gaps and no extra findings for that fixture.

These fixtures were created alongside the rules. Because the reviewer and examples share the same assumptions, this evaluation is a **development check**, not a held-out benchmark or a real-world accuracy score. The app does not currently ingest or learn from a customer dataset.

### How to collect better evaluation examples

1. **Define the purpose first.** Decide which checklist behaviors and failure types you need to measure.
2. **Get permission.** Use only documents you are authorized to evaluate. Prefer synthetic examples or explicitly approved, de-identified PRDs.
3. **Minimize data.** Remove names, email addresses, phone numbers, customer identifiers, secrets, and confidential details. The app’s masking is limited and must not be treated as comprehensive anonymization.
4. **Build variety.** Include strong, weak, borderline, short, long, different-domain, AI, non-AI, and edge-case PRDs—not just examples that resemble the rules.
5. **Label with people.** Have qualified reviewers independently identify each gap and severity, then resolve disagreements. Keep the evidence quote and reason for every label.
6. **Separate development and evaluation.** Use one set to tune rules and a separate, held-out set to estimate performance. Do not tune rules against the held-out results.
7. **Measure both misses and noise.** Track precision, recall, false positives, and false negatives overall and per check. A single score can hide an important weakness.
8. **Protect the set.** Limit access and retention, document consent and permitted use, and never send it to an external model without approval.
9. **Review changes over time.** Re-run the same held-out set when rules or prompts change, and create new examples for failures found in real use.

## 8. Edge cases and how they are handled

| Edge case | Current handling | Limitation to keep in mind |
|---|---|---|
| Empty review input | Validation returns an error. | User still needs to provide a real PRD. |
| Very short input | Requires at least eight words. | A short but valid summary may be blocked; this threshold is heuristic. |
| Non-English-looking text | A simple language heuristic may reject it. | English detection is not a full language detector and can misclassify text. |
| Oversized text | Input is bounded to 20,000 characters; the app warns when truncation occurs. Draft intake has a bounded budget across fields. | Important context near the end can be lost. Review and verify the truncated text. |
| Email/phone in text | Common email and phone patterns are masked before AI use. | This does not detect every personal identifier, secret, or sensitive detail. |
| Confidential-looking words | A warning is shown; AI use is blocked until a separate confirmation is checked. | Detection only catches configured phrases. Confirmation is not authorization; avoid sending confidential material. |
| Prompt-injection-like wording in notes | The app warns that instruction-like text is treated as source data; AI prompts also describe source text as untrusted. | This reduces risk but cannot guarantee an AI model will always ignore malicious instructions. |
| No API key | AI is skipped and a local draft/rules-based review remains available. | AI-specific additions are unavailable. |
| AI timeout, SDK error, or invalid response | The app reports an AI warning and keeps a local fallback or rules result. Malformed JSON gets one retry. | Model output can still be incomplete or wrong even when valid JSON. |
| AI invents a draft number | The AI draft is rejected if its numeric values do not occur in the source; the skeleton is shown instead. | Non-numeric unsupported claims still require human review. |
| AI review changes or invents a quote | Findings without an exact source quote or known check ID are dropped. Quotes affected by redaction are discarded if they no longer match the original. | This may discard a legitimate but altered quote; local checklist review remains available. |
| Goal conflicts with notes | A simple overlap check warns about likely conflicts when notes label non-goals. | It detects lexical overlap, not meaning, and only inspects labeled note lines. |
| Headings claim a check is satisfied | Headings alone do not count as evidence. | Body-text keyword matches can still be misleading. |
| No matching sample is selected | The app asks the user to choose a sample. | Samples are for demonstration, not required for normal use. |
| Browser session ends | Draft/review state is held in Streamlit session state, not a project database. | Do not assume work is a permanent saved copy; download/export important work. |

## 9. What could go wrong

- **False pass:** A keyword appears in a PRD, but the requirement is not actually satisfied. Example: “monitor” appears without a useful monitoring plan.
- **False finding:** The PRD explains something in different words and the keyword rule misses it.
- **Bad or misleading AI text:** A model may misunderstand notes, omit nuance, or produce fluent but incorrect wording.
- **Truncated context:** The app may remove text after the input limit.
- **Privacy exposure:** Basic email/phone masking may miss other identifying or confidential information sent after opt-in.
- **Misread score:** A higher checklist score can be mistaken for quality, readiness, or safety approval. It is only a count of checks passed by simple logic.
- **Lost work:** Session state is not a durable document store.
- **Configuration drift:** Local and hosted deployments may use different model names, secrets, dependencies, or policies.
- **Evaluation overconfidence:** The known planted flaws were authored with the rules, so success on them does not predict performance on unseen PRDs.

For consequential features, ask domain experts to review requirements, data handling, model behavior, tests, and launch plans. Never use the checklist as the only approval gate.

## 10. How the work maps to PM and AI skills

This table separates capabilities visible in the project from work that is not evidenced by the repository.

| Step | PM/product skill shown | AI/technical skill shown | Tools / evidence |
|---|---|---|---|
| Identify a product problem | Frames missing PRD decisions as a user/team problem; states a product hypothesis. | N/A | Product framing in this document; user research evidence remains a future need. |
| Define scope | Defines goals, features, non-goals, and AI/non-AI behavior. | Separates deterministic checks from optional model use. | PRD requirements; Streamlit controls. |
| Design the PRD workflow | Structures intake around problem, user, evidence, goal, and constraints. | Uses a fixed section schema and leaves gaps as open questions. | Python dataclasses and Markdown draft template. |
| Design review criteria | Groups checks by product decisions and assigns severity. | Uses reproducible local rules and excludes headings/open questions as evidence. | Checklist module and reviewer. |
| Add AI responsibly | Makes AI optional and provides a no-AI path. | Treats source text as untrusted, masks common direct identifiers, constrains JSON, checks output shape/numbers, and validates exact quotes. | Anthropic SDK, model prompts, validation and review modules. |
| Plan quality evaluation | Uses explicit examples of intended good and flawed PRDs. | Tests planted gaps and quote-verification behavior. | pytest and evaluation fixture. |
| Ship and operate | Provides a browser workflow, warnings, and Markdown export. | Bounds input and requests and provides fallbacks. | Streamlit, environment configuration, tests. |
| Learn after launch | Not yet shown: no user interviews, feedback loop, adoption analytics, or production evaluation data are documented. | Not yet shown: no held-out dataset, model comparison, or ongoing quality monitoring. | Recommended next phase, not a completed capability. |

## 11. Improvements, in practical order

### Before relying on results

1. **Evaluate on unseen PRDs.** Collect an approved, de-identified benchmark and human labels; report precision and recall per check.
2. **Improve rule meaning and evidence.** Require evidence in relevant sections, handle negation and contradictions, and test alternate wording.
3. **Test sensitive-data handling.** Add cases for addresses, account numbers, tokens, names, and other data types; consider a stronger approved data-loss-prevention solution.
4. **Explain scores clearly.** State that the score is a heuristic checklist score and show what a pass means and does not mean.
5. **Test AI failure modes.** Add evaluations for prompt injection, unsupported claims, conflicting notes, malformed outputs, and language variation.

### Improve daily usability

6. Save drafts explicitly to a user-selected local file or an approved storage service, with clear retention and delete controls.
7. Add editable AI drafts and a visible change/diff view so users can compare AI suggestions with source notes.
8. Let teams configure checklist wording and severity while recording the checklist version used.
9. Add accessibility checks, clearer truncation previews, and better handling for supported languages.
10. Add product feedback (useful/not useful and reason) with consent, and analyze it without collecting unnecessary PRD content.

### Improve team readiness

11. Add authenticated team workspaces, role-based access, audit logs, retention policies, and approved integrations only when the need and security design are established.
12. Add operational monitoring for latency, failures, cost, and opt-in AI usage, without logging raw PRDs by default.
13. Document the deployment process, owner, incident path, dependency updates, and model-change review.

## 12. How to verify the project

Run the automated tests:

```powershell
python -m pytest
```

Run the sample evaluation:

```powershell
python -m prdiq.evaluation
```

The evaluation output is limited to the planted fixture. A passing test suite means the tested code paths match the tests; it does not establish real-world checklist accuracy, privacy compliance, or model safety.

## 13. Interview preparation

Use these questions to explain the project. Be accurate about what is implemented versus planned.

### Product and PM questions

1. **What problem does PRDIQ solve?**  
   It helps teams draft and review PRDs so common requirements—especially AI evaluation, fallback, privacy, and human review—are less likely to be overlooked.

2. **Who is the target user?**  
   Product managers and teams writing or reviewing requirements. The repository does not prove this through completed user research, so I would validate the target with interviews.

3. **Why did you build both drafting and review?**  
   Drafting helps create a structured starting point; review checks an existing document. Together they cover creation and quality-checking.

4. **How would you measure success?**  
   Measure task completion and time saved, then usefulness and human-judged finding precision/recall. Set a baseline and targets after collecting real, permissioned data.

5. **What is out of scope?**  
   Automated approval, replacing human judgment, user accounts, team collaboration, persistent document storage, and integrations are not in the current v1.

6. **How did you prioritize the checklist?**  
   It covers decisions that make requirements actionable: problem/users, scope, testability, metrics, AI behavior, risk, privacy, rollout, and rollback. The criteria should be refined with actual users and domain experts.

7. **What would you improve first?**  
   Evaluate on a held-out set of real-world-style PRDs with independent human labels, because current fixtures are intentionally authored and cannot establish accuracy.

### AI and engineering questions

8. **Why use rules and AI instead of AI alone?**  
   Rules are local, repeatable, and explainable. AI can add semantic review, but it is optional and constrained; a failure still leaves a useful deterministic result.

9. **How do you reduce hallucinations in drafts?**  
   Prompt the model to use only source facts, leave gaps as open questions, validate the response schema, reject unsupported numbers, and fall back to a skeleton when the draft request fails. Human review is still necessary.

10. **How do you verify AI review findings?**  
    Findings must use an existing checklist ID and an exact quote present in the original source; duplicates are filtered.

11. **How do you handle prompt injection?**  
    Treat pasted text as untrusted source material, warn on some instruction-like phrases, and tell the model not to treat source text as instructions. This is defense-in-depth, not a guarantee.

12. **How do you handle privacy?**  
    AI use is opt-in, common email and phone patterns are redacted, suspicious confidentiality wording triggers a warning and confirmation, and the app advises against sensitive input. The masking is incomplete, so sensitive text should not be sent.

13. **What happens if the model or API fails?**  
    Drafting shows the open-question skeleton; review keeps the local rule results. The user sees a warning. Requests have a timeout and malformed JSON gets one retry.

14. **Is the system trained on the sample PRDs?**  
    No. They are local illustrative test fixtures; there is no training pipeline in this project.

15. **What does 24/24 mean?**  
    All 24 configured checks matched the current rule patterns for an AI-feature PRD. It does not mean the document is objectively complete, accurate, safe, or ready to launch.

16. **How do you know the checker is accurate?**  
    We do not know from these fixtures alone. They test expected behavior on authored examples. Accuracy requires unseen examples, human labels, and false-positive/false-negative analysis.

17. **What would you monitor in production?**  
    Completion, latency, errors, opt-in rate, finding usefulness, human-judged quality, and privacy/safety guardrails, while avoiding raw-document logging by default.

18. **What is the biggest technical limitation?**  
    The deterministic reviewer is largely keyword/pattern-based, so context, negation, wording differences, and contradictions can cause false passes or misses.

19. **How would you make it more accurate?**  
    Build a diverse, permissioned, independently labeled, held-out evaluation set; refine rules or prompts against development data; measure precision/recall by criterion; and re-check regressions after each change.

20. **What did you learn as a PM/AI builder?**  
    Good AI product requirements specify the user outcome and workflow as well as evaluation, limitations, privacy, fallback, human control, rollout, monitoring, and rollback. A fluent model response is not evidence that a product requirement is satisfied.

### A simple end-to-end interview story

“I built PRDIQ to help teams catch missing decisions in PRDs, with special attention to AI features. A user can start from notes or review an existing PRD. The local checklist provides repeatable findings and quotes; optional Anthropic calls can help draft or add review findings. I added safeguards such as explicit AI opt-in, input limits, basic email/phone masking, output checks, quote verification, and non-AI fallbacks. I also learned that passing a small set of deliberately planted examples is only a development check. My next priority would be a permissioned, independently labeled test set and user research to establish whether the tool saves time and produces useful findings.”

## 14. Project file map

- [app.py](./app.py): Streamlit interface, forms, session state, AI opt-in, and export.
- [prdiq/drafter.py](./prdiq/drafter.py): Draft sections, open questions, and draft-output checks.
- [prdiq/checklist.py](./prdiq/checklist.py): Checklist questions and severities.
- [prdiq/rules.py](./prdiq/rules.py): Deterministic checks, score, findings, and quote handling.
- [prdiq/reviewer.py](./prdiq/reviewer.py): Optional AI review and exact-quote verification.
- [prdiq/validation.py](./prdiq/validation.py): Input limits, language/confidentiality warnings, redaction, and conflict check.
- [prdiq/llm.py](./prdiq/llm.py): Anthropic/Gemini request adapter and JSON parsing/retry.
- [prdiq/evaluation.py](./prdiq/evaluation.py): Planted-flaw fixture evaluation.
- [sample_data/](./sample_data): Fictional example PRDs and expected planted flaws.
- [tests/](./tests): Automated behavior tests.
- [requirements.txt](./requirements.txt): Python package requirements.
- [.env.example](./.env.example): Empty configuration example; do not put a real secret here.