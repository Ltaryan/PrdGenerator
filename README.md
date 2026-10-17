# PRDIQ

PRDIQ is a draft-and-review tool for AI-feature PRDs. Drafting keeps missing details visible as `OPEN QUESTION`s; review checks a PRD against a deterministic 24-point checklist and verifies every displayed quote against the text. Markdown export works without an API key.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
streamlit run app.py
```

On macOS or Linux, activate with `source .venv/bin/activate`.

## Optional AI mode

AI is off unless a user opts in for an action. Two providers are supported; put one key in a local `.env` file (copy `.env.example`), the environment, or Streamlit secrets:

| Provider | Key | Model setting (default) | Cost |
|---|---|---|---|
| Anthropic Claude | `ANTHROPIC_API_KEY` | `ANTHROPIC_MODEL` (`claude-sonnet-4-5`) | Paid |
| Google Gemini | `GEMINI_API_KEY` ([get one](https://aistudio.google.com/apikey)) | `GEMINI_MODEL` (`gemini-3.6-flash`) | Free tier |

If both keys are set, Anthropic is used unless `AI_PROVIDER=gemini`. The app names the active provider wherever text may be sent. Inputs are sent to that provider only after explicit consent. Emails and phone numbers are redacted first, but do not paste employer-confidential or sensitive data. Each browser session is limited to six counted AI requests (including any malformed-JSON retry), each request is capped at 20,000 characters, and requests time out after 30 seconds. Gemini's free tier often answers "model overloaded"; those calls are retried briefly before falling back.

If the key is missing or an API call fails, drafting returns the open-question skeleton and review remains rule-based. Malformed model JSON is retried once. AI draft output is rejected if it does not match the section schema or introduces a numeric value absent from the source. AI review findings are dropped unless their exact quote occurs in the reviewed PRD.

## Review checklist

The 24 checks are grouped into problem and users, goals and scope, requirements, metrics and evaluation, AI behavior and safeguards, and risk, privacy, and rollout. Six checks apply only when the PRD describes an AI feature. Findings are deterministic, explainable, and quote a verbatim source line; headings and `OPEN QUESTION` lines do not count as evidence.

## Evaluation and limits

Run `python -m prdiq.evaluation` to compare the rule reviewer with the deliberately planted flaws in `sample_data/prd_flawed.md`. `prd_good.md` is an illustrative fictional sample, not a provided or validated InstaResolve PRD. The evaluation fixtures were written alongside the rules, so their results are development checks, not held-out accuracy or evidence of real-world usefulness. Test with real PRDs and record false alarms before making performance claims. PRDIQ helps expose structure and gaps; it does not replace product judgment.

## Not in v1

No accounts, database, team sharing, Jira integration, or Notion sync.


Planning documents: [3-month roadmap](docs/ROADMAP.md) and [experiment plan for AI review](docs/EXPERIMENT_PLAN.md).

See [PRD.md](./PRD.md) for the complete product requirements, step-by-step operating guide, sample-data and evaluation explanation, edge cases, improvement ideas, and interview preparation.
