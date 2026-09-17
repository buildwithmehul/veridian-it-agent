# Project Spec — Veridian IT Service Agent

## Problem
Employees submit short, messy IT requests. The agent must understand the issue, locate the relevant policy, ask only necessary questions, resolve simple requests, escalate risky/unclear requests, create structured tickets, show sources, and preserve an audit trail.

## Guardrails
1. The Veridian data pack is the source of truth.
2. Never invent an approval, SLA, owner, system, or policy.
3. Security incidents are escalated immediately and the user is told not to forward suspicious material.
4. Missing information produces a follow-up question rather than a guessed action.
5. Policy conflicts are surfaced. In particular, laptop replacement has a 3-year eligibility rule and a separate 4-year refresh/early-replacement Finance sign-off rule.

## Decision model
- Classify intent
- Retrieve top policy matches
- Detect risk / missing information
- Apply policy-specific decision rules
- Generate response
- Optionally create ticket
- Persist audit context

## Acceptance tests
| Scenario | Expected behavior |
|---|---|
| Password, 6 failures | Escalate for manual unlock; no approval |
| Guest Wi-Fi | Explain kiosk + 24h validity; no ticket |
| VPN contractor | Manager approval route |
| Non-catalog software | Security review; 3–5 business days |
| Phishing | Immediate Security route; do not forward |
| Admin server access | Escalate; do not invent policy |
| Vague request | Ask what service/device and error |
| Home office >3 days | Manager sign-off + Finance; IT shipping after approval |
| Mailbox full | Archive old mail; >25GB requires manager approval, max 50GB |
| Printer | Queue + spooler first; then ticket with asset tag |
