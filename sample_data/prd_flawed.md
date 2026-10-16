# Sample PRD: Receipt Sorting Assistant

## Problem and users
The problem is that small-business bookkeepers spend time sorting emailed receipts before monthly close.
Small-business bookkeepers are the primary users when reconciling transactions.
Evidence from interviews and support tickets shows repeated manual categorization work.
Today, bookkeepers manually rename receipt files and enter totals into the ledger.

## Goals and scope
Goal: reduce median receipt sorting time by 20% for the pilot cohort.
Version 1 scope includes suggested categories for emailed receipts.
Constraints: the feature depends on the existing ledger import API and mobile upload flow.

## Requirements
The user can review a suggested category and correct it before importing the receipt.
If an attachment is invalid or the import API returns an error, show an error state and preserve the receipt.
Owner: Finance Product is responsible for the launch decision.

## Metrics and evaluation
Success metric: target a 20% reduction in median sorting time against the baseline.
Baseline is measured from the analytics dashboard using import events.
Guardrail metrics include the false-positive categorization rate below a 3% threshold.

## AI behavior and safeguards
The AI model classifies receipt category from visible merchant and line-item text; confidence can be low for blurry images.
The model must not invent receipt totals or expose restricted financial data.

## Risk, privacy, and rollout
Risk: a wrong category could misstate a report; mitigation is review before import.
Rollout begins with a pilot and expands gradually after support-ticket review.