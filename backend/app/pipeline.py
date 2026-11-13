from pathlib import Path
from .config import STORAGE_DIR
from .graph import PIPELINE

def run_pipeline(job_id, request, update):
    work=STORAGE_DIR/job_id;work.mkdir(parents=True,exist_ok=True)
    state={"job_id":job_id,"request":request,"work_dir":str(work),"update":update}
    final=PIPELINE.invoke(state)
    return final["result"]
