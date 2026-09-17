# Veridian IT Service Agent

A grounded internal employee-support agent built for **AIONOS Agentic AI Factory — Assignment 2**.

## What it demonstrates
- Understands employee IT issues
- Retrieves only supplied Veridian policies/data
- Applies explicit routing rules for common cases
- Asks follow-up questions when key information is missing
- Resolves simple self-service requests
- Escalates risky/unclear requests
- Creates structured AI-generated tickets
- Shows source/context IDs used for the answer
- Keeps a visible request/ticket/policy/audit surface

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Data grounding
The data pack explicitly says to use only the supplied material and not invent policies. The prototype therefore keeps the knowledge base and ticket/request records local in `data/` and exposes source IDs in every agent decision.

Every agent response is persisted to `data/audit.json`. Created tickets include category, priority, source policy, action, escalation state, and ticket status.

## Architecture

`Employee -> Streamlit UI -> Intent Router -> Policy Retriever -> Decision/Risk Engine -> Response / Follow-up / Ticket -> Audit surface`

The current six-hour prototype intentionally uses a deterministic policy/decision layer instead of letting an LLM invent approvals. An LLM can be added as a presentation/orchestration layer without changing the policy constraints.

## Demo scenarios
1. Locked account after 6 attempts → IT unlock escalation
2. Guest Wi-Fi → self-service resolution
3. 3.5-year dead laptop → replacement route with asset-policy check
4. Phishing → immediate Security escalation
5. Home-office monitor → manager + Finance workflow
6. Admin access → escalation because the supplied policy is silent
7. Vague “it’s not working” → follow-up instead of guessing

## AI usage disclosure
AI assistance was used for project planning, architecture, code generation/refactoring, test-scenario design, and documentation. The final policy decisions were grounded against the supplied AIONOS assignment brief and Veridian data pack.
