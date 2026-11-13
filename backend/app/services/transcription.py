from pathlib import Path
from openai import OpenAI
from ..config import OPENAI_API_KEY, ENABLE_WHISPER

def _stamp(value):
    ms=int(value*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def _write_srt(items, output):
    blocks=[]
    for i,item in enumerate(items,1):
        text=(item.get("text") or "").strip()
        if text:blocks.append(f"{i}\n{_stamp(item['start'])} --> {_stamp(item['end'])}\n{text}")
    Path(output).write_text("\n\n".join(blocks),encoding="utf-8")

def create_captions(audio_path, output, scenes, fallback_duration):
    if ENABLE_WHISPER and OPENAI_API_KEY:
        try:
            client=OpenAI(api_key=OPENAI_API_KEY)
            with open(audio_path,"rb") as audio:
                result=client.audio.transcriptions.create(
                    model="whisper-1",file=audio,response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            segments=getattr(result,"segments",None) or []
            items=[{"start":s.start,"end":s.end,"text":s.text} for s in segments]
            if items:
                _write_srt(items,output);return "whisper"
        except Exception:
            pass
    # Deterministic fallback: scene captions distributed by word count.
    weights=[max(1,len(x.get("narration","").split())) for x in scenes]; total=sum(weights) or 1; cursor=0; items=[]
    for scene,w in zip(scenes,weights):
        end=cursor+fallback_duration*w/total
        items.append({"start":cursor,"end":end,"text":scene.get("narration","")})
        cursor=end
    _write_srt(items,output)
    return "estimated"
