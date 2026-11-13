# ShortsAI — Multi-Agent YouTube Shorts Studio

A portfolio-grade, agentic video-generation pipeline: topic → research → script → quality review → voice → visuals → Whisper captions → FFmpeg render.

## What's in this
- **LangGraph orchestration** with explicit research, writing, quality-control, voice, visual, transcription and rendering nodes.
- **Quality-control agent** checks factual grounding, hook, pacing and duration; requests one script revision when needed.
- **Whisper transcription** generates timestamped word/segment captions aligned to the generated narration.
- **AI-generated scene images** using the OpenAI Images API, with Pexels stock-photo and designed-card fallbacks.
- **Optional background music** from a file you have rights to use, mixed and ducked under narration.
- **SQLite job persistence**, Dockerfiles and Docker Compose.
- React dashboard, FastAPI API, downloadable MP4 and generation metadata.

## Architecture
`React → FastAPI → SQLite job queue → LangGraph`
`Research → Script Writer → QC/Revision → Voice → Visuals → Whisper → Render → MP4`

## Requirements
- Python 3.11+
- Node.js 20+ (local frontend development)
- FFmpeg + ffprobe (local mode); Docker Compose installs FFmpeg in the API container
- OpenAI API key (LLM + image generation + Whisper transcription)
- Optional Tavily API key (web research)
- Optional Pexels API key (stock-photo fallback)

## Run with Docker (recommended)
1. Copy `backend/.env.example` to `backend/.env` and add `OPENAI_API_KEY`.
2. Optional: add `TAVILY_API_KEY`, `PEXELS_API_KEY`, and set `IMAGE_PROVIDER=openai`.
3. Put a licensed music file at `backend/assets/background_music.mp3` (optional).
4. Run:
   ```bash
   docker compose up --build
   ```
5. Open http://localhost:5173. API docs: http://localhost:8000/docs.

## Run locally
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
uvicorn app.main:app --reload
```
### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Configuration
See `backend/.env.example`.
- `OPENAI_API_KEY`: required.
- `OPENAI_MODEL`: defaults to `gpt-4o-mini`.
- `IMAGE_PROVIDER`: `openai` or `pexels`; defaults to `openai`.
- `ENABLE_WHISPER`: defaults to `true`.
- `MUSIC_FILE`: optional path to a music file you are licensed to use.
- `TAVILY_API_KEY`, `PEXELS_API_KEY`: optional.

Image generation and Whisper incur API costs. To use stock images instead of generated images, set `IMAGE_PROVIDER=pexels` and provide a Pexels key. If no visual provider works, designed scene cards are generated locally.

## API
- `POST /api/generate` — enqueue a job.
- `GET /api/jobs/{job_id}` — persisted job status, stage, progress and result.
- `GET /api/videos/{job_id}` — download the MP4.
- `GET /api/health` — health check.

## GitHub
```bash
git init
git add .
git commit -m "Build ShortsAI v2 multi-agent video generator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shortsai.git
git push -u origin main
```
Never commit `.env`, API keys, generated videos, local databases or licensed media.

## Important publishing notes
- Generated scripts can contain errors. Review the source notes and final narration before publishing.
- Use only images, video and music that you are licensed or permitted to use. Check provider terms and attribution requirements.
- The app creates an MP4; it does not auto-publish to YouTube.
- This is an extensible portfolio MVP, not a production-scale hosted service. Add auth, rate limiting, cloud object storage and managed task workers before public deployment.
