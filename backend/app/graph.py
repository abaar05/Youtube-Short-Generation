from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from .services.research import research_topic
from .services.script_writer import create_script, review_and_revise
from .services.voice import generate_voiceover
from .services.visuals import create_scene_images
from .services.transcription import create_captions
from .services.render import render_video

class PipelineState(TypedDict, total=False):
    job_id: str
    request: Any
    work_dir: str
    update: Any
    research: list
    plan: dict
    qc: dict
    audio_path: str
    image_paths: list
    captions_path: str
    video_path: str
    result: dict

def research_node(state):
    state["update"]("Research agent", 10, "Gathering source notes.")
    state["research"] = research_topic(state["request"].topic)
    return state

def script_node(state):
    state["update"]("Script writer agent", 23, "Writing the hook, narration and scene plan.")
    state["plan"] = create_script(state["request"].topic, int(state["request"].duration), state["request"].style, state.get("research", []))
    return state

def quality_node(state):
    state["update"]("Quality-control agent", 32, "Checking factual grounding, pacing and structure.")
    revised, report = review_and_revise(state["plan"], state.get("research", []), int(state["request"].duration))
    state["plan"], state["qc"] = revised, report
    return state

def voice_node(state):
    state["update"]("Voice agent", 43, "Generating narration audio.")
    plan = state["plan"]
    narration = " ".join([plan.get("hook",""), *[s.get("narration","") for s in plan.get("scenes",[])] ]).strip()
    path = str(__import__("pathlib").Path(state["work_dir"]) / "voice.mp3")
    generate_voiceover(narration, state["request"].voice, path)
    state["audio_path"] = path
    return state

def visuals_node(state):
    state["update"]("Visual agent", 58, "Creating AI visuals or retrieving stock-photo fallbacks.")
    paths = create_scene_images(state["plan"]["scenes"], __import__("pathlib").Path(state["work_dir"]) / "visuals",
                                use_ai=state["request"].use_ai_images)
    state["image_paths"] = [str(p) for p in paths]
    return state

def captions_node(state):
    state["update"]("Whisper transcription agent", 73, "Transcribing narration and aligning captions.")
    path = str(__import__("pathlib").Path(state["work_dir"]) / "captions.srt")
    create_captions(state["audio_path"], path, state["plan"]["scenes"], int(state["request"].duration))
    state["captions_path"] = path
    return state

def render_node(state):
    state["update"]("Video rendering agent", 86, "Rendering vertical MP4, captions and optional music.")
    from .config import MUSIC_FILE, BASE_DIR
    music = (BASE_DIR / MUSIC_FILE).resolve()
    if not state["request"].use_music or not music.is_file(): music = None
    out = str(__import__("pathlib").Path(state["work_dir"]) / "shortsai_video.mp4")
    render_video(state["image_paths"], state["audio_path"], state["captions_path"], out,
                 int(state["request"].duration), str(music) if music else None)
    state["video_path"] = out
    plan = state["plan"]
    state["result"] = {
        "video_url": f"/api/videos/{state['job_id']}", "title": plan.get("title", state["request"].topic),
        "description": plan.get("description",""), "hashtags": plan.get("hashtags",[]),
        "script": plan.get("script",""), "sources": state.get("research",[]),
        "quality_report": state.get("qc",{}), "captions": "captions.srt"
    }
    return state

def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("research", research_node)
    graph.add_node("script", script_node)
    graph.add_node("quality", quality_node)
    graph.add_node("voice", voice_node)
    graph.add_node("visuals", visuals_node)
    graph.add_node("captions", captions_node)
    graph.add_node("render", render_node)
    graph.set_entry_point("research")
    graph.add_edge("research","script")
    graph.add_edge("script","quality")
    graph.add_edge("quality","voice")
    graph.add_edge("voice","visuals")
    graph.add_edge("visuals","captions")
    graph.add_edge("captions","render")
    graph.add_edge("render",END)
    return graph.compile()

PIPELINE = build_graph()
