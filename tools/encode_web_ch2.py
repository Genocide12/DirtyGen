#!/usr/bin/env python3
"""Веб-кодирование CH 02 NIGHT: .build_film/ch2_film.mp4 -> video/ch2_night.mp4.

Куски по 900 кадров (resume), затем склейка + мукс с готовым звуком.
Цель: < 95 МБ, H.264 High@4.0, 48 кГц, faststart.
Запуск: python3 tools/encode_web_ch2.py
"""
import os, subprocess, sys, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(BASE, ".build_film")
SRC = os.path.join(BUILD, "ch2_film.mp4")
DST = os.path.join(BASE, "video", "ch2_night.mp4")
CH = os.path.join(BUILD, "web_ch2")
os.makedirs(CH, exist_ok=True)

V = ["-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
     "-preset", "fast", "-crf", "21",
     "-maxrate", "2.8M", "-bufsize", "5.6M",
     "-pix_fmt", "yuv420p", "-g", "60", "-keyint_min", "6",
     "-r", "30", "-fps_mode", "cfr", "-video_track_timescale", "15360"]

dur = 217.300
total = int(round(dur * 30))
CF = 900
n = (total + CF - 1) // CF
print(f"веб-кодирование ch2: {total} кадров, {n} чанков")


def run(cmd, tag):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr)
        raise SystemExit(f"{tag} fail")
    print(f"[{tag}] ok", flush=True)


files = []
src_mt = os.path.getmtime(SRC)
for i in range(n):
    cp = os.path.join(CH, f"w{i:02d}.mp4")
    files.append(cp)
    if os.path.exists(cp) and os.path.getsize(cp) > 10000 and os.getmtime(cp) > src_mt:
        continue  # чанк свежее источника — валиден
    st = i * 30.0
    fr = min(CF, total - i * CF)
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{st:.3f}", "-i", SRC,
         "-an"] + V + ["-frames:v", str(fr), cp], f"w{i:02d}")

lst = os.path.join(CH, "list.txt")
with open(lst, "w") as fp:
    for p in files:
        fp.write(f"file '{p}'\n")
cat = os.path.join(CH, "cat.mp4")
if not (os.path.exists(cat) and os.path.getsize(cat) > 1e6
        and os.path.getmtime(cat) > src_mt):
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", cat], "concat")

# звук берём готовым из ch2_film (уже с помехами), видео — новая сборка
run(["ffmpeg", "-y", "-v", "error", "-i", cat, "-i", SRC,
     "-map", "0:v:0", "-map", "1:a:0",
     "-c:v", "copy", "-c:a", "copy",
     "-movflags", "+faststart", DST], "mux")

p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration,size:stream=codec_name,level,sample_rate",
                    "-of", "json", DST], capture_output=True, text=True)
j = json.loads(p.stdout)
mb = float(j["format"]["size"]) / 1e6
print(json.dumps(j, indent=1)[:600])
print(f"ГОТОВО: video/ch2_night.mp4  {mb:.1f} MB  {j['format']['duration']}s")
if mb > 98:
    raise SystemExit("ПРЕВЫШЕН ЛИМИТ 100 МБ — ужать сильнее")
