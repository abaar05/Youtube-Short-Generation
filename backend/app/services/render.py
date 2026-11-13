from pathlib import Path
import shutil, subprocess

def render_video(images,audio,srt,output,duration,music=None):
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg:raise RuntimeError("FFmpeg not found. Install FFmpeg or use Docker Compose.")
    work=Path(output).parent; concat=work/"images.txt"; per=duration/max(1,len(images))
    lines=[]
    for p in images:
        safe=str(Path(p).resolve()).replace("'","'\\''")
        lines += [f"file '{safe}'",f"duration {per:.3f}"]
    last=str(Path(images[-1]).resolve()).replace("'","'\\''");lines.append(f"file '{last}'")
    concat.write_text("\n".join(lines),encoding="utf-8")
    # The subtitle file is in the working directory. FFmpeg's subtitles filter renders captions into the picture.
    subtitle=Path(srt).name.replace("\\","/").replace(":","\\:").replace("'","\\'")
    vf=f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{subtitle}':force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=150'"
    cmd=[ffmpeg,"-y","-f","concat","-safe","0","-i",str(concat),"-i",str(audio)]
    if music:
        cmd += ["-stream_loop","-1","-i",str(music),"-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]","-map","0:v","-map","[aout]"]
    else:cmd += ["-map","0:v","-map","1:a"]
    cmd += ["-vf",vf,"-t",str(duration),"-r","30","-c:v","libx264","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest",str(output)]
    result=subprocess.run(cmd,cwd=work,capture_output=True,text=True)
    if result.returncode:raise RuntimeError("FFmpeg render failed: "+result.stderr[-2000:])
