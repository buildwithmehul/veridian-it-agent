import os, json

def llm_available():
    return bool(os.getenv('OPENAI_API_KEY'))

def rewrite_grounded(query, draft, source_texts):
    """Optional LLM presentation layer. It never supplies policy facts; it only rewrites grounded facts."""
    if not llm_available():
        return draft
    try:
        from openai import OpenAI
        client=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        model=os.getenv('OPENAI_MODEL','gpt-4o-mini')
        prompt=(
            'You are the response-writing layer of an internal IT support agent. '
            'Use ONLY the supplied source text and the draft decision. Do not add policies, approvals, SLAs, owners, URLs, or technical steps. '
            'Preserve escalation and uncertainty exactly. Be concise and professional.\n\n'
            f'EMPLOYEE REQUEST:\n{query}\n\nDRAFT DECISION:\n{draft}\n\n'
            f'SOURCES:\n{json.dumps(source_texts, ensure_ascii=False)}\n\n'
            'Return only the final employee-facing response.'
        )
        resp=client.chat.completions.create(model=model,messages=[{'role':'system','content':'You are a grounded IT support response writer.'},{'role':'user','content':prompt}],temperature=0)
        return resp.choices[0].message.content.strip() or draft
    except Exception:
        return draft
