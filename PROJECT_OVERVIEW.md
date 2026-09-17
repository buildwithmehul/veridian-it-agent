# Veridian IT Internal Service Agent

Repository: [github.com/buildwithmehul/veridian-it-agent](https://github.com/buildwithmehul/veridian-it-agent)

## Purpose

A grounded internal IT support agent for Veridian Corp, built for the AIONOS Assignment 2 brief.

The agent uses only the supplied assignment data pack and does not invent policies, approvals, owners, SLAs, or external information.

## Technology

- Python
- Streamlit
- JSON files
- Deterministic rule-based decision engine
- Optional OpenAI response-rewriting layer
- No database
- No vector database
- No real ticketing API
- No authentication
- No email sending
- No external knowledge source

Dependencies are defined in [requirements.txt](requirements.txt).

## Data included

The project contains the supplied data pack:

- 11 policies in [data/policies.json](data/policies.json)
- 15 employee requests in [data/requests.json](data/requests.json)
- 10 original ticket records in [data/tickets.json](data/tickets.json)
- Clean audit-log baseline in [data/audit.json](data/audit.json)

The supplied policy set covers:

- Password reset
- VPN access
- Laptop replacement
- Software installation
- Printer troubleshooting
- Mailbox quota
- Guest Wi-Fi
- Expense software access
- Security incident reporting
- Work-from-home equipment
- Asset-management refresh policy

## Architecture

```text
Employee
   |
   v
Streamlit interface
   |
   v
Intent classifier
   |
   v
Policy selection / retrieval
   |
   v
Risk and information checks
   |
   v
Decision engine
   |
   +--> Resolve
   |
   +--> Ask follow-up
   |
   +--> Escalate
   |
   +--> Create structured ticket
   |
   v
Source display + audit trail
```

The main implementation is in [src/agent.py](src/agent.py), and the UI is in [app.py](app.py).

## Agent workflow

### 1. Employee submits an issue

The user enters:

- Employee name
- Employee email
- IT issue description

### 2. Intent classification

The agent identifies one of the supported request types:

- Password
- VPN
- Laptop
- Software
- Printer
- Mailbox
- Guest Wi-Fi
- Expense tool
- Security incident
- Home-office equipment
- Admin access
- Unknown/ambiguous

### 3. Relevant policy selection

The agent maps the request to the relevant supplied policy IDs.

Examples:

- Password issue -> `KB-01`
- VPN issue -> `KB-02`
- Laptop replacement -> `KB-03` and `ASSET-01`
- Phishing -> `KB-09`
- Guest Wi-Fi -> `KB-07`

Admin-access and unclear requests do not receive invented policy sources.

### 4. Decision

The agent produces one of three actions:

- `resolve`
- `follow_up`
- `escalate`

### 5. Response

The employee receives:

- Explanation of the decision
- Applicable policy guidance
- Follow-up questions where information is missing
- Escalation explanation where human review is required
- Source policy IDs

### 6. Ticket creation

For escalation or follow-up cases, the reviewer can create a structured AI ticket containing:

- Ticket ID
- Employee
- Email
- Issue
- Category
- Priority
- Status
- Source policy
- Action taken
- Escalated flag
- Risk
- Created timestamp
- Source/context list

Tickets created by the prototype use IDs such as `AI-0001`.

## Implemented policy behavior

### Password reset

- Self-service reset is explained.
- More than five failed attempts routes to manual IT unlock.
- No approval is invented or required.

### VPN

- Full-time employee access is treated as automatic.
- Contractor access requires manager approval through the access request form.
- Expired credentials require employee renewal.

### Laptop

- Three years or more supports replacement routing.
- Hardware failure can support earlier replacement.
- Hardware verification is requested where needed.
- The separate four-year asset refresh and Finance sign-off rule is included.

### Software

- Catalog software can be self-installed.
- Non-catalog software is routed to Security review.
- The supplied 3-5 business-day review period is preserved.

### Printer

- Check the print queue.
- Restart the print spooler.
- If unresolved, create a ticket containing the printer asset tag.

### Mailbox

- Default quota is 25GB.
- Archiving old mail is recommended.
- Increases above 25GB require manager approval.
- Maximum quota is 50GB.

### Guest Wi-Fi

- Employee can generate credentials at the front-desk kiosk.
- Credentials last 24 hours.
- No IT ticket is required.

### Expense software

- Finance grants access.
- IT only assists with technical/login issues once an account exists.
- The agent asks whether an account exists and requests the exact error.

### Security incidents

- Phishing, malware, and unauthorized access are treated as critical.
- The employee is directed to `security@veridian-corp.example`.
- The employee is told not to forward the suspicious message.
- The request is escalated to Security.

### Work-from-home equipment

- More than three remote days per week qualifies for the supplied allowance.
- Manager sign-off and Finance processing are required.
- IT handles shipping only after approval.

### Admin access

- No supplied policy defines approval for finance-server admin access.
- The agent does not invent an approval process.
- The request is escalated with the limitation clearly stated.

### Ambiguous request

For messages such as "it's not working," the agent asks:

- What service or device is affected?
- What exact error or symptom is shown?

## Existing ticket queue processing

The assignment says active supplied tickets must also be processed.

The implementation processes these four active tickets through the same decision engine:

- `TK-1043` - laptop replacement -> escalate using `KB-03` and `ASSET-01`
- `TK-1044` - non-catalog software -> escalate using `KB-04`
- `TK-1047` - home-office equipment -> escalate using `KB-10`
- `TK-1048` - phishing report -> escalate using `KB-09`

Closed, rejected, and approved historical tickets remain context only.

## User interface

The Streamlit interface provides:

### Chat tab

- Employee details
- Issue input
- Agent response
- Intent
- Action
- Risk
- Follow-up questions
- Source/context IDs
- Structured ticket creation

### Policies tab

Displays the complete supplied knowledge base.

### Employee Requests tab

Displays all 15 supplied employee requests and their original initial actions.

### Ticket Queue tab

Displays:

- Original supplied tickets
- Active-ticket agent action
- Source policy
- Escalation state
- Risk

It also includes the **Clear Created Tickets** button.

This button removes only tickets whose IDs begin with `AI-`. It never removes the original `TK-1042` through `TK-1051` records.

### Audit Trail tab

Stores and displays:

- Conversation ID
- User message
- Agent response
- Intent
- Decision
- Source policy
- Follow-up questions
- Ticket status
- Timestamp

## Testing

Automated tests are in [tests/test_agent.py](tests/test_agent.py).

The test suite validates:

- Dataset counts
- All REQ-01 through REQ-15 scenarios
- Intent classification
- Expected action for each request
- Expected source policy for each request
- Audit record creation
- Ticket schema
- Follow-up behavior
- Exact five-attempt password boundary
- Active-ticket processing
- Safe removal of created tickets
- Preservation of all 10 supplied tickets

Current validation result:

```text
Ran 6 tests
OK
```

Manual UI testing also verified:

- Guest Wi-Fi resolution
- Password lockout escalation
- Structured ticket creation
- Audit trail visibility
- Ticket queue display
- Created-ticket cleanup
- Preservation of original ticket history

## Documentation

The repository includes:

- [README.md](README.md)
- [PROJECT_SPEC.md](PROJECT_SPEC.md)
- [AIONOS_Assignment2_PRD.md](AIONOS_Assignment2_PRD.md)
- [AIONOS_Assignment2_TODO.md](AIONOS_Assignment2_TODO.md)
- [AIONOS_Assignment2_Build_Spec.md](AIONOS_Assignment2_Build_Spec.md)
- [tests.md](tests.md)
- Supplied assignment PDF

## Running locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL in a browser.

## GitHub delivery

The project is published with a professional commit history covering:

- Repository setup
- Supplied data
- Agent engine
- Streamlit UI
- Tests
- Documentation
- Created-ticket cleanup

The repository is available at:

[https://github.com/buildwithmehul/veridian-it-agent](https://github.com/buildwithmehul/veridian-it-agent)
