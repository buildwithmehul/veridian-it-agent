# Demo / QA Checklist

- [x] Guest Wi-Fi returns no-ticket self-service guidance.
- [x] Password after >5 failed attempts routes to manual IT unlock.
- [x] Phishing is critical and includes security@veridian-corp.example and no-forward instruction.
- [x] Admin access does not invent an approval process.
- [x] Vague request asks clarifying questions.
- [x] Sources are visible for each decision.
- [x] Escalation/follow-up can create a structured AI ticket.
- [x] Existing active/closed ticket context is visible in the UI.

## Automated validation

Run all prescribed REQ-01 through REQ-15 scenarios:

```bash
python -m unittest discover -s tests -v
```
