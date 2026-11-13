import json
from openai import OpenAI
from ..config import OPENAI_API_KEY, OPENAI_MODEL

def _client():
    if not OPENAI_API_KEY: raise RuntimeError("OPENAI_API_KEY is missing. Configure backend/.env.")
    return OpenAI(api_key=OPENAI_API_KEY)

def create_script(topic, duration, style, research):
    context="\n\n".join(f"SOURCE: {x.get('title')}\nURL: {x.get('url')}\nNOTES: {x.get('content')}" for x in research) or "No external research retrieved. Avoid unsupported factual claims."
    prompt=f'''Create a YouTube Short about {topic}. Style={style}; target={duration} seconds.
Use sources as grounding; never invent statistics or quotes. Create 5-8 scenes.
Return JSON only with: title, hook, script, scenes (array of narration, visual_query, caption), description, hashtags.
Research:
{context}'''
    r=_client().chat.completions.create(model=OPENAI_MODEL,messages=[{"role":"system","content":"You are a careful short-form video scriptwriter. Return valid JSON only."},{"role":"user","content":prompt}],response_format={"type":"json_object"},temperature=0.65)
    return json.loads(r.choices[0].message.content)

def review_and_revise(plan, research, duration):
    context="\n".join(f"{x.get('title')}: {x.get('content','')[:900]}" for x in research)
    prompt=f'''Review this short video script for factual support, clarity, hook strength, pacing for {duration}s, and scene coverage.
Sources: {context or "No external sources retrieved."}
Draft JSON: {json.dumps(plan)}
Return JSON only: {{"approved":true/false,"issues":["..."],"revised_plan":{{same schema as draft}},"score":0-100}}.
Keep claims conservative. If draft is already good, return it unchanged.'''
    try:
        r=_client().chat.completions.create(model=OPENAI_MODEL,messages=[{"role":"system","content":"You are a strict editorial quality-control reviewer. Return valid JSON only."},{"role":"user","content":prompt}],response_format={"type":"json_object"},temperature=0.2)
        report=json.loads(r.choices[0].message.content)
        return report.get("revised_plan") or plan, {"approved":report.get("approved",False),"issues":report.get("issues",[]),"score":report.get("score")}
    except Exception as exc:
        return plan, {"approved":False,"issues":[f"QC unavailable: {exc}"],"score":None}
