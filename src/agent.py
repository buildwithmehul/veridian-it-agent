import json, re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / 'data/policies.json', encoding='utf-8') as f: POLICIES = json.load(f)
with open(ROOT / 'data/requests.json', encoding='utf-8') as f: REQUESTS = json.load(f)
with open(ROOT / 'data/tickets.json', encoding='utf-8') as f: TICKETS = json.load(f)
AUDIT_PATH = ROOT / 'data/audit.json'
if AUDIT_PATH.exists():
    with open(AUDIT_PATH, encoding='utf-8') as f: AUDIT_LOG = json.load(f)
else:
    AUDIT_LOG = []

STOPWORDS = set('the a an is are to for of my your me can i get it this that and or how do need please what with on in at from'.split())

def retrieve(query, k=3):
    q = set(re.findall(r"[a-z0-9]+", query.lower())) - STOPWORDS
    scored=[]
    for p in POLICIES:
        text=(p['title']+' '+p['text']+' '+' '.join(p['tags'])).lower()
        toks=set(re.findall(r"[a-z0-9]+", text))
        overlap=len(q & toks)
        phrase_bonus=sum(2 for tag in p['tags'] if tag in query.lower())
        scored.append((overlap+phrase_bonus,p))
    return [p for s,p in sorted(scored,key=lambda x:x[0],reverse=True)[:k] if s>0]

def lookup_context(query):
    q=query.lower(); out=[]; identifiers=set(re.findall(r"[a-z0-9._-]+", q))
    for r in REQUESTS:
        known={r['id'].lower(), r['employee'].lower(), r['email'].lower()}
        if known & identifiers or any(value in q for value in known if ' ' in value):
            out.append(('request',r))
    for t in TICKETS:
        known={t['id'].lower(), t['employee'].lower()}
        if known & identifiers or any(value in q for value in known if ' ' in value):
            out.append(('ticket',t))
    return out[:5]

def classify(q):
    x=q.lower()
    if any(w in x for w in ['phishing','malware','unauthorized access','suspicious email']): return 'security_incident'
    if 'guest' in x and ('wifi' in x or 'wi-fi' in x): return 'guest_wifi'
    if 'vpn' in x: return 'vpn'
    if ('password' in x or 'account' in x) and any(w in x for w in ['locked','reset','failed','login']): return 'password'
    if 'laptop' in x and any(w in x for w in ['replace','replacement','dead','won’t turn','wont turn','flicker','flickering','broken']): return 'laptop'
    if 'printer' in x or 'paper jam' in x or 'spooler' in x: return 'printer'
    if ('software' in x or 'extension' in x) and any(w in x for w in ['install','installation','catalog','approval']): return 'software'
    if 'mailbox' in x or ('email' in x and any(w in x for w in ['full','quota','storage'])): return 'mailbox'
    if 'home' in x and any(w in x for w in ['monitor','chair','equipment','office']): return 'home_office'
    if 'expense' in x: return 'expense'
    if 'admin access' in x or ('access' in x and 'server' in x): return 'admin_access'
    return 'unclear'

def answer(query, conversation_id='default', record_audit=True):
    intent=classify(query)
    intent_sources={
        'password':['KB-01'], 'vpn':['KB-02'], 'laptop':['KB-03','ASSET-01'],
        'software':['KB-04'], 'printer':['KB-05'], 'mailbox':['KB-06'],
        'guest_wifi':['KB-07'], 'expense':['KB-08'], 'security_incident':['KB-09'],
        'home_office':['KB-10'], 'admin_access':[], 'unclear':[]
    }
    policies=[p for p in POLICIES if p['id'] in intent_sources.get(intent,[])]
    if not policies and intent not in ('admin_access', 'unclear'):
        policies=retrieve(query,3)
    ctx=lookup_context(query)
    sources=[p['id'] for p in policies]
    risk='low'; action='answer'; ticket=None; follow=[]

    if intent=='security_incident':
        risk='critical'; action='escalate'
        text='This is a security incident. Report the suspected phishing email, malware, or unauthorized access immediately to security@veridian-corp.example. Do not forward it to other employees. Because the request involves a suspected security incident, I would route this to Security rather than resolve it as a normal IT request.'
    elif intent=='guest_wifi':
        text='Guest Wi-Fi does not require an IT ticket. An employee can generate credentials from the front-desk kiosk; the credentials are valid for 24 hours.'
        action='resolve'
    elif intent=='password':
        m_attempts=re.search(r'(?:password\s*)?(\d+)\s*(?:failed\s*)?(?:password\s*)?(?:attempts|tries|times)', query.lower())
        too_many=bool(m_attempts and int(m_attempts.group(1))>5)
        if too_many:
            text='Because the account was tried more than 5 times and is locked, IT needs to unlock it manually. No approval is required. I would route this to IT for manual unlock.'
            action='escalate'; risk='medium'
        else:
            text='You can reset your password through the self-service portal at any time. If you are locked out after 5 failed attempts, IT must unlock the account manually; no approval is required.'
            action='resolve'
    elif intent=='vpn':
        if 'contractor' in query.lower():
            text='Contractors require manager approval submitted through the access request form. Full-time employees receive VPN access automatically. VPN credentials expire every 90 days and must be renewed by the employee.'
            action='escalate'; risk='medium'
        else:
            text='VPN access is automatic for full-time employees. If the credentials have expired, they must be renewed by the employee. If renewal does not resolve the issue, I would collect the error details and route the technical issue to IT.'
            action='resolve'
    elif intent=='software':
        text='If the software or browser extension is not in the approved catalog, it requires IT Security review. The stated review time is 3–5 business days. I cannot approve the installation myself.'
        action='escalate'; risk='medium'
    elif intent=='printer':
        text='First check the printer queue and restart the print spooler. If the problem persists, create an IT ticket and include the printer asset tag. I would not claim the printer is fixed without that check.'
        action='resolve'
    elif intent=='mailbox':
        text='The default mailbox quota is 25GB. First archive old mail. If you need more than 25GB, manager approval is required and the maximum quota is 50GB.'
        action='resolve'
    elif intent=='home_office':
        text='Employees working remotely more than 3 days per week are eligible for a one-time home-office equipment allowance for a chair or monitor. Manager sign-off and Finance processing are required. IT handles shipping only after approval.'
        action='escalate'; risk='medium'
    elif intent=='expense':
        text='Expense-tool access is granted by Finance, not IT. IT can help with login or technical issues once an account already exists. For an invalid-credentials issue, I would first confirm that the employee already has an active account and collect the relevant error details.'
        action='follow_up'; follow=['Do you already have an active expense-tool account?','What exact error message do you see?']
    elif intent=='laptop':
        years=None
        m=re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',query.lower())
        if m: years=float(m.group(1))
        failure=any(w in query.lower() for w in ['dead','won’t turn','wont turn','flicker','flickering','hardware failure'])
        if years is not None and years>=3:
            text='The supplied policy says laptops are eligible for replacement after 3 years, or earlier for verified hardware failure. Requests should be raised at least 2 weeks before intended replacement. The separate asset policy states a 4-year refresh cycle and requires Finance sign-off for early replacement outside that cycle. I would therefore verify the hardware failure and route the replacement through IT, with Finance sign-off if it is treated as an early replacement under the asset policy.'
            action='escalate'; risk='medium'
        elif failure:
            text='The policy allows replacement earlier than 3 years when there is verified hardware failure. For a flickering or dead laptop, I would first verify the hardware failure rather than assume replacement is approved. If replacement is requested, the asset policy also states that early replacement outside the 4-year refresh cycle requires Finance sign-off.'
            action='follow_up'; follow=['Can you confirm whether the hardware failure has been verified by IT?','Is the request for repair only, or are you requesting replacement?']
        else:
            text='Laptop replacement is normally eligible after 3 years. Earlier replacement requires verified hardware failure, and replacement requests should be raised at least 2 weeks in advance. The asset policy also describes a 4-year refresh cycle and Finance sign-off for early replacement outside that cycle.'
            action='follow_up'; follow=['How old is the laptop?','Is the hardware failure verified by IT?']
    elif intent=='admin_access':
        text='The supplied IT knowledge base does not define an admin-access approval policy for the finance reporting server. I would not invent an approval rule or grant access. This request should be escalated to the appropriate human owner with the business justification and required access scope recorded.'
        action='escalate'; risk='high'
    else:
        text='I need one more detail to route this correctly. Please describe what is not working (for example: laptop, VPN, printer, mailbox, software, password, or expense tool) and include any error message you see.'
        action='follow_up'; risk='medium'; follow=['What service or device is affected?','What exact error or symptom do you see?']

    if ctx:
        sources += [f"{typ.upper()}:{obj['id']}" for typ,obj in ctx]
    sources=list(dict.fromkeys(sources))
    source_texts=[p['id']+': '+p['text'] for p in policies]
    try:
        from .llm import rewrite_grounded
        text=rewrite_grounded(query,text,source_texts)
    except Exception:
        pass
    result={'response':text,'intent':intent,'action':action,'risk':risk,'sources':sources,'follow_up':follow,'context':ctx}
    audit_record={
        'id': f'AUD-{len(AUDIT_LOG)+1:04d}',
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'user_message': query,
        'decision': action,
        'intent': intent,
        'conversation_id': conversation_id,
        'user_message': query,
        'response': text,
        'source_policy': [source for source in sources if not source.startswith(('REQUEST:', 'TICKET:'))],
        'follow_up': follow,
        'ticket_status': 'Not created'
    }
    if record_audit:
        AUDIT_LOG.append(audit_record)
        with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
            json.dump(AUDIT_LOG, f, indent=2)
        result['audit_id']=audit_record['id']
    else:
        result['audit_id']=None
    return result

def process_active_tickets():
    """Apply the same policy workflow to supplied tickets still marked active."""
    processed=[]
    for ticket in TICKETS:
        if '(active)' not in ticket['status'].lower():
            continue
        result=answer(ticket['issue'], conversation_id=f"TICKET-{ticket['id']}", record_audit=False)
        processed.append({
            **ticket,
            'action': result['action'],
            'source_policy': [source for source in result['sources'] if not source.startswith(('REQUEST:', 'TICKET:'))],
            'escalated': result['action'] == 'escalate',
            'risk': result['risk']
        })
    return processed

def create_ticket(employee, email, query, result):
    active=[t for t in TICKETS if t['id'].startswith('AI-')]
    num=1+max([int(t['id'].split('-')[1]) for t in active],default=0)
    ticket_id=f'AI-{num:04d}'
    ticket={
        'id': ticket_id,
        'employee': employee or 'Employee',
        'email': email or 'not provided',
        'issue': query,
        'category': result['intent'],
        'priority': 'Critical' if result['risk'] == 'critical' else ('High' if result['risk'] == 'high' else ('Medium' if result['risk'] == 'medium' else 'Low')),
        'status': 'Open — routed by AI agent',
        'source_policy': [source for source in result['sources'] if not source.startswith(('REQUEST:', 'TICKET:'))],
        'action_taken': result['action'],
        'escalated': result['action'] == 'escalate',
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'risk': result['risk'],
        'sources': result['sources']
    }
    TICKETS.append(ticket)
    with open(ROOT / 'data/tickets.json','w',encoding='utf-8') as f: json.dump(TICKETS,f,indent=2)
    for record in AUDIT_LOG:
        if record['id'] == result.get('audit_id'):
            record['ticket_status'] = ticket['status']
            break
    with open(AUDIT_PATH, 'w', encoding='utf-8') as f:
        json.dump(AUDIT_LOG, f, indent=2)
    return ticket
