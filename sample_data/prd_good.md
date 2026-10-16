# Sample PRD: InstaResolve Support Triage

## Problem and users
The problem is that support agents spend too much time finding the right prior answer, delaying resolution for customers.
Support agents are the primary users while handling incoming tickets in the support console.
Evidence: interviews with 12 agents and a review of support ticket data show repeated searches across the same knowledge base.
Today, agents manually search old tickets and copy a workaround into the current workflow.

## Goals and scope
Goal: reduce median time to a verified first response by 20% within the pilot cohort.
Non-goals: autonomous sending of replies, changing ticket priority, and replacing agent judgment.
Version 1 scope includes AI-generated answer suggestions with links to cited internal sources.
Constraints: the feature depends on the existing ticket API and must use the approved model endpoint.

## Requirements
The user can request a suggested answer, inspect its sources, edit it, and choose whether to send it.
Acceptance criteria: Given a ticket with a matching source, when an agent requests a suggestion, then the system shows a cited draft within 2 seconds.
If the source search fails or the model times out, show an error state and keep the existing ticket workflow available.
Owner: Support Product is responsible for launch decisions.

## Metrics and evaluation
Success metric: target a 20% reduction in median time to verified first response against the current baseline.
Baseline comes from the analytics dashboard using the ticket-created and first-response events.
Evaluation uses a representative test set of resolved tickets with a quality review by support specialists.
Guardrail metrics include false-positive source citations below a 2% threshold and the escalation rate.

## AI behavior and safeguards
The AI model retrieves relevant internal content and generates a draft; confidence is limited when sources are incomplete.
Fallback: when the model is unavailable or confidence is low, the agent uses the current manual workflow.
Human review is required before any suggested answer is sent; the agent can edit or reject it.
The model must not invent citations, expose restricted content, or make commitments on behalf of the company.

## Risk, privacy, and rollout
Privacy: ticket personal data is redacted before model use, access is restricted, and prompt retention is disabled.
Risk: stale knowledge may produce a misleading answer; mitigation is source citation and agent review.
Rollout starts with a pilot cohort, then expands gradually after the quality review.
Monitor citation accuracy and latency; alert the owner and rollback by disabling suggestions if a threshold is exceeded.