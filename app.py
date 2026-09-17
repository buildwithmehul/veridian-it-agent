import streamlit as st
from uuid import uuid4
from src.agent import answer, clear_created_tickets, create_ticket, process_active_tickets, POLICIES, REQUESTS, TICKETS, AUDIT_LOG

st.set_page_config(page_title='Veridian IT Service Agent', page_icon='🛠️', layout='wide')

st.markdown('''<style>
.block-container{padding-top:1.5rem;max-width:1200px}
.small{color:#667085;font-size:.9rem}
.source{background:#f4f7fb;border:1px solid #dce3ed;padding:.5rem .7rem;border-radius:8px;margin:.25rem 0}
</style>''', unsafe_allow_html=True)

st.title('🛠️ Veridian IT Service Agent')
st.caption('A grounded internal-support agent for the AIONOS Assignment 2 — IT Support use case')

with st.sidebar:
    st.header('Agent controls')
    employee=st.text_input('Employee name', value='Demo Employee')
    email=st.text_input('Employee email', value='demo@veridian-corp.example')
    st.divider()
    st.markdown('**Safety design**')
    st.write('• Policy-grounded retrieval\n• Deterministic routing for risky cases\n• No invented approvals\n• Source IDs shown\n• Ticket creation + audit log')
    st.divider()
    st.markdown('**Quick scenarios**')
    examples=[
        'My account is locked after 6 password attempts',
        'I need guest Wi-Fi for tomorrow',
        'My laptop is dead and it is 3.5 years old',
        'I think I got a phishing email asking for my login',
        'I need a monitor because I work from home 4 days a week',
        'Can you give me admin access to the finance reporting server?'
    ]
    for e in examples:
        if st.button(e, use_container_width=True): st.session_state['query']=e

if 'query' not in st.session_state: st.session_state['query']=''
if 'conversation_id' not in st.session_state: st.session_state['conversation_id']=f'CONV-{uuid4().hex[:8]}'

left,right=st.columns([2.2,1])
with left:
    st.subheader('Ask IT')
    query=st.text_area('Describe your issue', value=st.session_state['query'], height=110, placeholder='Example: My VPN says my credentials expired.')
    c1,c2=st.columns([1,1])
    run=c1.button('Run agent', type='primary', use_container_width=True)
    clear=c2.button('Clear', use_container_width=True)
    if clear: st.session_state['query']=''; st.rerun()

if run and query.strip():
    result=answer(query.strip(), st.session_state['conversation_id'])
    st.session_state['last_result']=result

if 'last_result' in st.session_state:
    r=st.session_state['last_result']
    st.divider(); st.subheader('Agent decision')
    a,b,c=st.columns(3)
    a.metric('Intent',r['intent'].replace('_',' ').title())
    b.metric('Action',r['action'].replace('_',' ').title())
    c.metric('Risk',r['risk'].upper())
    st.info(r['response'])
    if r['follow_up']:
        st.markdown('**Follow-up questions**')
        for q in r['follow_up']: st.write('• '+q)
    st.markdown('**Sources / context used**')
    for s in r['sources']: st.markdown(f'<div class="source">{s}</div>', unsafe_allow_html=True)
    if r['action'] in ('escalate','follow_up'):
        if st.button('Create structured ticket', type='secondary'):
            t=create_ticket(employee,email,query,r)
            st.success(f"Created {t['id']} — {t['status']}")
    else:
        st.caption('No ticket is required for a simple, self-service resolution unless the employee asks for escalation.')

with right:
    st.subheader('Agent state')
    st.metric('Policies',len(POLICIES))
    st.metric('Employee requests',len(REQUESTS))
    st.metric('Tickets',len(TICKETS))
    st.caption('Assignment data is embedded locally. The agent is intentionally constrained to the supplied data pack.')

st.divider()
t1,t2,t3,t4=st.tabs(['Request Queue','Ticket Queue','Knowledge Base','Audit Trail'])
with t1:
    st.dataframe(REQUESTS, use_container_width=True, hide_index=True)
with t2:
    if st.button('Clear Created Tickets', help='Remove AI-created test tickets only; the 10 supplied tickets are preserved.'):
        TICKETS = clear_created_tickets()
        st.success('Created test tickets cleared. The supplied ticket history was preserved.')
    st.dataframe(process_active_tickets() + [t for t in TICKETS if '(active)' not in t['status'].lower()], use_container_width=True, hide_index=True)
with t3:
    st.dataframe([{'ID':p['id'],'Policy':p['title'],'Source text':p['text']} for p in POLICIES], use_container_width=True, hide_index=True)
with t4:
    st.dataframe(AUDIT_LOG, use_container_width=True, hide_index=True)

st.divider()
st.caption('Audit principle: every response exposes the policy/context IDs that drove the decision; the agent does not invent missing policy.')
