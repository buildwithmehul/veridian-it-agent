
# CODEX PROMPTS — BUILD PROJECT FROM SCRATCH

## Prompt 1 — Project Setup

Create a Streamlit project named `veridian-it-agent`.

Tech stack:
- Python
- Streamlit
- JSON
- No database.

Folder structure:
app.py
src/
data/
assets/
README.md
requirements.txt

Do not generate extra features.

---

## Prompt 2 — Data Layer

Convert the supplied AIONOS data pack into three JSON files.

1. policies.json
2. requests.json
3. tickets.json

Copy every policy, request and ticket exactly as provided.

Do not invent fields or modify content.

---

## Prompt 3 — Intent Router

Build a deterministic intent classifier.

Supported intents:
- password_reset
- vpn
- laptop
- software_install
- printer
- mailbox
- guest_wifi
- expense_tool
- security_incident
- wfh_equipment
- unknown

Return one intent only.

---

## Prompt 4 — Policy Retrieval

Given an intent, retrieve matching policy.

Return:
- policy_id
- title
- policy_text

Use only policies.json.

---

## Prompt 5 — Decision Engine

Implement rules.

Possible outputs:
- RESOLVE
- FOLLOW_UP
- ESCALATE

Never invent approvals or policies.

Return:
action
reason
source_policy

---

## Prompt 6 — Follow-Up Questions

Ask follow-up questions only when information is missing.

Examples:
- Unknown issue.
- Missing asset tag.
- Missing contractor approval.
- Missing screenshot.

No unnecessary questions.

---

## Prompt 7 — Ticket Generator

Create structured tickets.

Fields:
ticket_id
employee_email
summary
status
action
source_policy
audit_entry

---

## Prompt 8 — Audit Trail

Maintain conversation history.

Each audit entry:
timestamp
user_message
agent_response
action
source_policy

---

## Prompt 9 — Streamlit UI

Build four tabs:
- Chat
- Policies
- Employee Requests
- Ticket Queue

Chat should display:
Issue
Decision
Source Policy
Ticket Created (if applicable)

---

## Prompt 10 — Testing

Test all 15 employee requests.

Expected behaviour:
Resolve simple requests.
Escalate risky requests.
Ask follow-up when information is insufficient.

No additional test cases outside supplied dataset.

---

## Prompt 11 — README

Write README containing:
Project overview.
Setup.
Run command.
Folder structure.
Features (only assignment features).
Demo instructions.

Nothing beyond assignment scope.
