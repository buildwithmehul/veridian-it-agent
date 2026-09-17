
# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Veridian IT Internal Service Agent — AIONOS Assignment 2

## Goal
Build an internal IT support agent for Veridian Corp using **only the supplied data pack**.

## Scope (Strict)
- 11 knowledge base policies.
- 15 employee requests.
- 10 existing ticket records.
- No external knowledge.
- No invented policies.
- No extra features.

## Functional Requirements
1. Understand employee issue.
2. Find relevant policy/resolution.
3. Ask sensible follow-up questions when needed.
4. Resolve simple requests.
5. Escalate risky or unclear requests.
6. Create a structured ticket.
7. Show policy source used.
8. Maintain conversation + action audit trail.

## Inputs
- Employee message.
- Knowledge base.
- Existing ticket queue.

## Outputs
- Response.
- Action taken.
- Source policy IDs.
- Ticket (if created/escalated).

## Out of Scope
- Authentication.
- Email sending.
- Real ticketing APIs.
- Vector databases.
- Extra company policies.
- HR/Finance agent.
- Analytics/dashboard.
