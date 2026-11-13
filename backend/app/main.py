from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from pathlib import Path
import threading
from .config import FRONTEND_ORIGIN,STORAGE_DIR
from .models import GenerateRequest
from .database import init_db,create_job,update_job,get_job
from .pipeline import run_pipeline

app=FastAPI(title="ShortsAI API",version="2.0.0",description="LangGraph multi-agent YouTube Shorts generator")
app.add_middleware(CORSMiddleware,allow_origins=[FRONTEND_ORIGIN,"http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
executor=ThreadPoolExecutor(max_workers=2)
lock=threading.Lock()

@app.on_event("startup")
def startup():init_db()

def progress(job_id,stage,value,message):
    with lock:update_job(job_id,status="completed" if value==100 else "processing",stage=stage,progress=value,message=message)

def process(job_id,request):
    try:
        result=run_pipeline(job_id,request,lambda s,p,m:progress(job_id,s,p,m))
        with lock:update_job(job_id,status="completed",stage="Completed",progress=100,message="Your Short is ready.",result_json=result)
    except Exception as exc:
        with lock:update_job(job_id,status="failed",stage="Failed",error=str(exc),message="Generation failed.")

@app.get("/api/health")
def health():return {"status":"ok","version":"2.0.0"}

@app.post("/api/generate")
def generate(request:GenerateRequest):
    job_id=uuid4().hex[:12];create_job(job_id,request);executor.submit(process,job_id,request)
    return {"job_id":job_id}

@app.get("/api/jobs/{job_id}")
def job_status(job_id):
    data=get_job(job_id)
    if not data:raise HTTPException(status_code=404,detail="Job not found")
    return data

@app.get("/api/videos/{job_id}")
def video(job_id):
    path=(STORAGE_DIR/job_id/"shortsai_video.mp4").resolve()
    if STORAGE_DIR.resolve() not in path.parents or not path.is_file():raise HTTPException(status_code=404,detail="Video not found")
    return FileResponse(path,media_type="video/mp4",filename="shortsai_video.mp4")
