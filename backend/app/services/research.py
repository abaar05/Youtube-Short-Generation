import requests
from ..config import TAVILY_API_KEY

def research_topic(topic: str) -> list[dict]:
    if TAVILY_API_KEY:
        try:
            r=requests.post("https://api.tavily.com/search",json={"api_key":TAVILY_API_KEY,"query":topic,"search_depth":"basic","max_results":5},timeout=20)
            r.raise_for_status()
            return [{"title":x.get("title","Source"),"url":x.get("url",""),"content":x.get("content","")[:1800]} for x in r.json().get("results",[])]
        except requests.RequestException: pass
    try:
        data=requests.get("https://en.wikipedia.org/w/api.php",params={"action":"query","list":"search","srsearch":topic,"format":"json"},timeout=15).json()
        notes=[]
        for item in data.get("query",{}).get("search",[])[:4]:
            title=item.get("title","")
            summary=requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",headers={"User-Agent":"ShortsAI/2.0"},timeout=15).json()
            notes.append({"title":title,"url":summary.get("content_urls",{}).get("desktop",{}).get("page",""),"content":summary.get("extract","")})
        return notes
    except Exception: return []
