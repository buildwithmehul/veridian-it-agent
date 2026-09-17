
# BUILD SPECIFICATION — WHAT WE HAVE TO BUILD

## Tech Stack
- Python
- Streamlit
- JSON files (no database)

## Dataset
- policies.json (11 policies)
- requests.json (15 requests)
- tickets.json (10 tickets)

## Screens

### Screen 1
Employee chat interface.

### Screen 2
Knowledge Base viewer.

### Screen 3
Employee Requests viewer.

### Screen 4
Ticket Queue viewer.

## Agent Flow
1. User enters issue.
2. Detect intent.
3. Match relevant policy.
4. Decide:
   - Resolve
   - Ask follow-up
   - Escalate
5. If required, create structured ticket.
6. Show source policy ID.
7. Save audit trail.

## Required Intents
- Password Reset
- VPN Access
- Laptop Replacement
- Software Installation
- Printer Issue
- Mailbox Quota
- Guest Wi-Fi
- Expense Tool Access
- Security Incident
- Work From Home Equipment
- Unknown / Ambiguous

## Ticket Object
- Ticket ID
- Employee
- Issue Summary
- Status
- Source Policy
- Action Taken
- Escalated (Yes/No)

## Submission Deliverables
- GitHub repo
- Working Streamlit app
- Demo video
- 10-slide PPT
