# Experiment plan: does AI review help PMs improve their PRDs?

> **Status: designed, not run.** PRDIQ is a portfolio project without a user base yet. This plan shows how the decision "should AI review be recommended?" would be tested. Inputs marked *assumption* must be replaced with real data. It depends on the "useful / not useful" feedback item in the [roadmap](ROADMAP.md).

## 1. Why this experiment

The rules-only review is free, instant and repeatable. AI review adds **4–6 quote-verified findings** per review on a sample PRD, but it costs money, sends text to a provider, and varies between runs. Verified is not the same as **useful**: we don't know whether the extra findings change what a PM writes.

## 2. Hypothesis

**If** users get AI review findings in addition to the rules, **then** more review sessions will lead to a real PRD change, **because** the AI catches weak or vague requirements that fixed rules miss.

## 3. Design

| Decision | Choice | Why |
|---|---|---|
| **Unit of randomisation** | Review session (user who clicks Review and has opted in to AI) | Only users willing to use AI are eligible, so we compare like with like |
| **Groups** | Control: rules-only findings. Treatment: rules + AI findings | Isolates the value of the AI layer |
| **Assignment** | Random 50/50 per session, sticky per browser | Prevents a user seeing both versions of the same PRD |
| **Consent** | Users have already opted in to AI; control users are told AI review is "queued" and can run it after giving feedback | Ethical: nobody is denied the feature permanently |
| **Duration** | Until the sample size is reached, at least 2 full weeks | Avoids day-of-week effects |

## 4. Metrics

| Type | Metric | Definition |
|---|---|---|
| **Primary** | Session "led to a change" rate | Review sessions where the user marks ≥ 1 finding "useful, I changed my PRD" ÷ review sessions |
| Secondary | Useful-finding share | Findings marked useful ÷ findings shown |
| Secondary | Re-review improvement | Fewer blockers when the same PRD is reviewed again |
| **Guardrail** | "Wrong finding" rate | Findings marked "not useful: incorrect" ÷ findings shown; must not rise by > 5 points |
| **Guardrail** | Abandonment | Sessions that leave before viewing findings |
| Guardrail | Cost and latency | AI cost per review; p90 review time under 30 s |

## 5. Sample size

Two-sided test, α = 0.05, power = 80%.

| Input | Value | Source |
|---|---|---|
| Baseline "led to a change" rate (rules only) | 40% | *assumption*: measure during the first month |
| Minimum detectable effect | +10 points (40% → 50%) | Smallest gain worth the AI cost and privacy trade-off |
| **Sessions needed** | **385 per group, 770 in total** | Two-proportion formula |

Sensitivity: detecting +15 points (40% → 55%) needs 171 sessions per group.

**Feasibility check:** a portfolio tool may not reach 770 sessions. If traffic is too low, run a **within-subject usability study** instead: 10–12 PMs each review two PRDs, one with and one without AI (order randomised), with outcomes rated by an independent reviewer. That's weaker evidence, but realistic.

## 6. Decision rule (agreed before launch)

| Result | Decision |
|---|---|
| Primary rises ≥ 10 points, significant, guardrails within limits | Recommend AI review to opted-in users by default (still opt-in) |
| Primary rises, but the wrong-finding rate rises > 5 points | Tighten AI prompts and quote rules; re-test |
| No significant change | Keep AI optional and invest in the rules |

## 7. Risks

- **Novelty bias:** users click "useful" on new AI findings out of curiosity. Mitigation: the primary metric requires "I changed my PRD", not just "useful".
- **Self-selection:** only AI-willing users are eligible, so results don't generalise to everyone. That's acceptable, because the decision is only about those users.
- **Feedback fatigue:** few users rate findings. Mitigation: one-click rating, and analyse rated sessions plus the response rate.
