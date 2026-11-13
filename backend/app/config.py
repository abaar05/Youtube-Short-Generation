import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "storage"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR = BASE_DIR / "assets"
ASSET_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = os.getenv("DATABASE_PATH", str(STORAGE_DIR / "shortsai.sqlite3"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai").lower()
ENABLE_WHISPER = os.getenv("ENABLE_WHISPER", "true").lower() == "true"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
MUSIC_FILE = os.getenv("MUSIC_FILE", "assets/background_music.mp3")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
