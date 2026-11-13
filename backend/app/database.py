import json, sqlite3
from pathlib import Path
from .config import DATABASE_PATH
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

def connect():
    db = sqlite3.connect(DATABASE_PATH, timeout=30)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY, status TEXT NOT NULL, stage TEXT NOT NULL,
            progress INTEGER NOT NULL, message TEXT NOT NULL, request_json TEXT NOT NULL,
            result_json TEXT, error TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

def create_job(job_id, request):
    with connect() as db:
        db.execute("INSERT INTO jobs(job_id,status,stage,progress,message,request_json) VALUES(?,?,?,?,?,?)",
                   (job_id,"queued","Queued",0,"Waiting to start.",request.model_dump_json()))

def update_job(job_id, **fields):
    allowed = {"status","stage","progress","message","result_json","error"}
    fields = {k:v for k,v in fields.items() if k in allowed}
    if not fields: return
    fields["updated_at"] = __import__("datetime").datetime.utcnow().isoformat()
    cols = ", ".join(f"{k}=?" for k in fields)
    vals = [json.dumps(v) if k == "result_json" and v is not None else v for k,v in fields.items()]
    with connect() as db:
        db.execute(f"UPDATE jobs SET {cols} WHERE job_id=?", (*vals,job_id))

def get_job(job_id):
    with connect() as db:
        row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if not row: return None
    item = dict(row)
    item["result"] = json.loads(item["result_json"]) if item.get("result_json") else None
    item.pop("result_json", None)
    item.pop("request_json", None)
    return item
