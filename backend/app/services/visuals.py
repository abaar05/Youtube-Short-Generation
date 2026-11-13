from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from ..config import OPENAI_API_KEY, IMAGE_PROVIDER, PEXELS_API_KEY

W,H=1080,1920
def _font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","C:/Windows/Fonts/arialbd.ttf"]:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def _card(text,path,index):
    im=Image.new("RGB",(W,H),(13+index*7,22+index*5,45+index*8)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((65,260,1015,1650),radius=50,outline=(105,145,230),width=5)
    words=text.split(); lines=[]; line=""
    for w in words:
        if len(line)+len(w)>19: lines.append(line); line=w
        else: line=(line+" "+w).strip()
    if line:lines.append(line)
    y=700
    for line in lines[:5]: d.text((110,y),line,font=_font(65),fill="white"); y+=95
    d.text((110,1760),"SHORTSAI • AI SCENE",font=_font(28),fill=(160,190,225))
    im.save(path,quality=92)

def _ai_image(prompt,path):
    if not OPENAI_API_KEY:return False
    try:
        client=OpenAI(api_key=OPENAI_API_KEY)
        response=client.images.generate(model="gpt-image-1",prompt=f"Create a cinematic vertical 9:16 background image for a YouTube Short. No text, no logos. Scene: {prompt}",size="1024x1536")
        import base64
        path.write_bytes(base64.b64decode(response.data[0].b64_json))
        with Image.open(path) as im: im.convert("RGB").resize((W,H)).save(path,quality=90)
        return True
    except Exception:return False

def _pexels(query,path):
    if not PEXELS_API_KEY:return False
    try:
        r=requests.get("https://api.pexels.com/v1/search",headers={"Authorization":PEXELS_API_KEY},params={"query":query,"orientation":"portrait","per_page":1},timeout=20);r.raise_for_status()
        photos=r.json().get("photos",[])
        if not photos:return False
        data=requests.get(photos[0]["src"]["large"],timeout=30).content;path.write_bytes(data)
        with Image.open(path) as im:
            im=im.convert("RGB"); iw,ih=im.size; target=W/H
            if iw/ih>target:
                nw=int(ih*target); left=(iw-nw)//2; im=im.crop((left,0,left+nw,ih))
            else:
                nh=int(iw/target); top=(ih-nh)//2; im=im.crop((0,top,iw,top+nh))
            im.resize((W,H)).save(path,quality=90)
        return True
    except Exception:return False

def create_scene_images(scenes,folder,use_ai=True):
    folder.mkdir(parents=True,exist_ok=True); paths=[]
    for i,scene in enumerate(scenes):
        p=folder/f"scene_{i:02d}.jpg"; query=scene.get("visual_query") or scene.get("caption") or "cinematic abstract background"
        ok=False
        if use_ai and IMAGE_PROVIDER=="openai":ok=_ai_image(query,p)
        if not ok:ok=_pexels(query,p)
        if not ok:_card(scene.get("caption") or query,p,i)
        paths.append(p)
    return paths
