#!/usr/bin/env python3
"""Сборка клипов Грязного Гены — универсальный сборщик под 3 трека.

Тайминги секций выведены из анализа энергии треков (analyze_track.py):
  clip1 «Я НЕ В СЕТИ» (185.64 c): дроп 52с, брейк 118с, пик 168-178
  clip2 «ТРЕК 2»      (214.03 c): дроп 80с, взрыв 198с
  clip3 «ТРЕК 3»      (258.74 c): брейк 136с, пульс-финал 224-256

Запуск:  python3 build_clip.py <clip1|clip2|clip3> <render|final>
Сегменты кэшируются: существующий файл с верной длительностью не рендерится.
"""
import hashlib, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = "/home/z/my-project/dirtygen"
F4K = f"{ROOT}/frames_4k"
AUD_DIR = "/home/z/my-project/upload"
FPS = 30

D = "noise=alls=16:allf=t:enable='between(t,0,0.45)'"      # глитч-шум на входе
RG = "rgbashift=rh=2:bv=-2"
RG2 = "rgbashift=rh=5:bv=-5"

# ============================================================
# КОНФИГИ КЛИПОВ
# ============================================================
CONFIGS = {}

# ---------- CLIP 1 · «Я НЕ В СЕТИ» · 185.64 c ----------
CONFIGS["clip1"] = dict(
    audio=f"{AUD_DIR}/Трек .mp3",
    out=f"{ROOT}/video/ya_ne_v_seti_clip.mp4",
    build=f"{ROOT}/.build1",
    title=("ГРЯЗНЫЙ ГЕНА", "Я НЕ В СЕТИ"),
    ch="CH 02",
    grade="",
    scenes=[
        # ИНТРО 0-16
        ("i1", 6.50, "01", "zin",   ""),
        ("i2", 6.50, "02", "zout",  ""),
        ("i3", 3.00, "03", "zin",   D),
        # КУПЛЕТ 1 · 16-46
        ("v1", 7.50, "04", "panLR", ""),
        ("v2", 7.50, "05", "zin",   ""),
        ("v3", 7.50, "06", "panRL", ""),
        ("v4", 7.50, "07", "panU",  ""),
        # ПРЕ-ДРОП · 46-52 (дроп на 52)
        ("p1", 3.10, "08", "zin",   ""),
        ("p2", 2.45, "09", "zout",  ""),
        ("st", 0.45, None, "static", ""),
        # ДРОП · 52-68
        ("d1", 4.20, "10", "zin_fast",   "noise=alls=14:allf=t:enable='between(t,0,0.3)'"),
        ("d2", 4.20, "11", "zin_fast",   ""),
        ("d3", 3.80, "12", "zout_fast",  RG),
        ("d4", 3.80, "13", "panLR_fast", RG2),
        # НЕОН-ЧАСТЬ ДРОПА · 68-82
        ("n1", 7.00, "14", "zout", ""),
        ("n2", 7.00, "15", "panU",  ""),
        # КУПЛЕТ 2 · 82-118
        ("k1", 5.00, "16", "zin",   ""),
        ("k2", 8.00, "17", "panRL", ""),
        ("k3", 8.00, "06", "zout",  ""),   # дубль: один против толпы
        ("k4", 8.00, "07", "panLR", ""),   # дубль: смотрит вверх
        ("k5", 7.00, "12", "zin",   ""),   # дубль: глаз («не заметили»)
        # БРЕЙК · 118-135
        ("b1", 8.00, "18", "zin",  "noise=alls=7:allf=t"),
        ("b2", 9.00, "19", "zout", ""),
        # БИЛД-АП · 135-156
        ("u1", 7.00, "20", "panU",  ""),
        ("u2", 7.00, "21", "zin",   ""),
        ("u3", 7.00, "22", "panLR", ""),
        # ФИНАЛ ч.1 · 156-163
        ("f1", 4.00, "23", "zin_fast",  ""),
        ("f2", 3.00, "26", "zout_fast", ""),
        # ПАУЗА + СТАТИК · 163-168
        ("q1", 4.55, "27", "zin", ""),
        ("s2", 0.45, None, "static", ""),
        # ГЛАВНЫЙ ПИК · 168-178
        ("g1", 5.00, "24", "zout_fast",  ""),
        ("g2", 5.00, "25", "panLR_fast", ""),
        # АУТРО + ТИТРЫ · 178-185.64
        ("o1", 4.64, "28", "zout", ""),
        ("tt", 3.00, None, "title", ""),
    ],
    fast={"p1", "p2", "d1", "d2", "d3", "f1", "f2", "g1", "g2"},
    soft={"n2", "b2"},
)

# ---------- CLIP 2 · «ТРЕК 2» · 214.03 c · неоновая версия ----------
CONFIGS["clip2"] = dict(
    audio=f"{AUD_DIR}/Трек2.mp3",
    out=f"{ROOT}/video/trek2_clip.mp4",
    build=f"{ROOT}/.build2",
    title=("ГРЯЗНЫЙ ГЕНА", "ТРЕК 2"),
    ch="CH 03",
    grade="eq=contrast=1.10:saturation=1.24:gamma=0.97",
    scenes=[
        # ИНТРО 0-13
        ("i1", 5.00, "03", "zin",   D),
        ("i2", 4.00, "01", "zout",  ""),
        ("i3", 4.00, "02", "panU",  ""),
        # КУПЛЕТ 1 · 13-36
        ("v1", 6.00, "14", "zin",   ""),
        ("v2", 6.00, "10", "panLR", ""),
        ("v3", 5.50, "12", "zout",  ""),
        ("v4", 5.50, "11", "zin",   ""),
        # ПАУЗА · 36-43
        ("p1", 4.00, "15", "zout", ""),
        ("p2", 3.00, "08", "zin",  ""),
        # ГРУВ · 43-73
        ("g1", 5.50, "13", "panLR_fast", RG2),
        ("g2", 6.50, "04", "panLR", ""),
        ("g3", 6.00, "05", "zin",   ""),
        ("g4", 6.00, "06", "panRL", ""),
        ("g5", 6.00, "07", "panU",  ""),
        # ПАУЗА · 73-80
        ("q1", 4.00, "16", "zin",  ""),
        ("q2", 3.00, "09", "zout", ""),
        # ДРОП 1 · 80-91
        ("d1", 5.50, "17", "zin_fast",  RG),
        ("d2", 5.50, "12", "zout_fast", ""),
        # КУПЛЕТ 2 · 91-139
        ("k1", 7.00, "18", "zin",   ""),
        ("k2", 7.00, "19", "zout",  ""),
        ("k3", 7.00, "02", "panRL", ""),
        ("k4", 7.00, "20", "panU",  ""),
        ("k5", 7.00, "21", "zin",   ""),
        ("k6", 7.00, "22", "panLR", ""),
        ("k7", 6.00, "04", "zout",  ""),
        # МОСТ · 139-153
        ("m1", 7.00, "27", "zout", ""),
        ("m2", 7.00, "07", "zin",  ""),
        # НАРАСТАНИЕ · 153-183
        ("r1", 6.00, "24", "zout_fast",  ""),
        ("r2", 6.00, "25", "panLR_fast", ""),
        ("r3", 6.00, "26", "zin",   ""),
        ("r4", 6.00, "13", "zout",  ""),
        ("r5", 6.00, "28", "panU",  ""),
        # СПАД · 183-197
        ("w1", 4.50, "08", "zout", ""),
        ("w2", 4.50, "09", "zin",  ""),
        ("w3", 5.00, "16", "zout", ""),
        # ВЗРЫВ · 197-214.03
        ("st", 0.45, None, "static", ""),
        ("x1", 5.00, "10", "zin_fast",   "noise=alls=14:allf=t:enable='between(t,0,0.3)'"),
        ("x2", 5.50, "11", "panLR_fast", RG2),
        ("x3", 6.08, "24", "zout_fast",  ""),
    ],
    fast={"p2", "g1", "q2", "d1", "d2", "r1", "r2", "x1", "x2"},
    soft={"q2", "w3", "m1"},
)

# ---------- CLIP 3 · «ТРЕК 3» · 258.74 c · полный фильм ----------
CONFIGS["clip3"] = dict(
    audio=f"{AUD_DIR}/Трек3.mp3",
    out=f"{ROOT}/video/trek3_clip.mp4",
    build=f"{ROOT}/.build3",
    title=("ГРЯЗНЫЙ ГЕНА", "ТРЕК 3"),
    ch="CH 04",
    grade="eq=contrast=1.06:saturation=1.12",
    scenes=[
        # ИНТРО 0-20
        ("i1", 7.00, "01", "zin",  ""),
        ("i2", 7.00, "02", "zout", ""),
        ("i3", 6.00, "03", "zin",  D),
        # КУПЛЕТ 1 · 20-54
        ("v1", 8.50, "04", "panLR", ""),
        ("v2", 8.50, "05", "zin",   ""),
        ("v3", 8.50, "06", "panRL", ""),
        ("v4", 8.50, "07", "panU",  ""),
        # ГРУВ · 54-66
        ("g1", 6.00, "10", "zin",   ""),
        ("g2", 6.00, "11", "panLR", ""),
        # ПАУЗА · 66-79
        ("p1", 6.50, "12", "zout", ""),
        ("p2", 6.50, "15", "zin",  ""),
        # ГРУВ 2 · 79-105
        ("h1", 6.50, "13", "panLR_fast", RG2),
        ("h2", 6.50, "14", "zout", ""),
        ("h3", 6.50, "16", "zin",  ""),
        ("h4", 6.50, "17", "panRL", ""),
        # МИНИ-ПРОВАЛ · 105-108.5
        ("x0", 3.50, "08", "zout", ""),
        # ГРУВ 3 · 108.5-134.5
        ("j1", 7.00, "18", "zin",   ""),
        ("j2", 7.00, "19", "zout",  ""),
        ("j3", 6.00, "05", "zout",  ""),
        ("j4", 6.00, "06", "zin",   ""),
        # БОЛЬШОЙ БРЕЙК · 134.5-153.74
        ("b1", 5.00, "03", "zout", ""),
        ("b2", 4.24, "08", "zin",  ""),
        ("b3", 5.00, "09", "panU", ""),
        ("b4", 5.00, "16", "panRL", ""),
        # ВОССТАНОВЛЕНИЕ · 153.74-201.74
        ("r1", 7.00, "20", "panU",  ""),
        ("r2", 7.00, "21", "zin",   ""),
        ("r3", 7.00, "22", "panLR", ""),
        ("r4", 7.00, "27", "zout",  ""),
        ("r5", 7.00, "28", "panU",  ""),
        ("r6", 6.50, "07", "zout",  ""),
        ("r7", 6.50, "12", "zin",   ""),
        # ПОДЪЁМ · 201.74-223.74
        ("u1", 6.00, "23", "zin_fast",  ""),
        ("u2", 6.00, "26", "zout_fast", ""),
        ("u3", 6.00, "25", "panLR_fast", ""),
        ("u4", 4.00, "24", "zout", ""),
        # ПУЛЬС-ФИНАЛ · 223.74-255.74 (взрывы 224/232/240/244/250/252)
        ("z1", 4.00, "13", "zin_fast",   RG),
        ("z2", 4.00, "11", "panLR_fast", ""),
        ("z3", 4.00, "26", "zout_fast",  ""),
        ("z4", 4.00, "24", "zin_fast",   ""),
        ("z5", 4.00, "23", "panLR_fast", RG2),
        ("z6", 4.00, "25", "zout_fast",  ""),
        ("z7", 4.00, "10", "zin_fast",   "noise=alls=10:allf=t:enable='between(t,0,0.25)'"),
        ("z8", 4.00, "24", "zout_fast",  ""),
        # КОНЦОВКА · 255.74-258.74
        ("tt", 3.00, None, "title", ""),
    ],
    fast={"x0", "h1", "u1", "u2", "u3", "z1", "z2", "z3", "z4", "z5", "z6", "z7"},
    soft={"p2", "b4", "r4"},
)

# ============================================================
# Титр-карточка (параметризованная, кэш по тексту)
# ============================================================
def make_title_card(line1, line2, build):
    key = hashlib.md5((line1 + line2).encode()).hexdigest()[:8]
    path = f"{build}/title_{key}.png"
    if os.path.exists(path):
        return path
    W, H = 3840, 2160
    img = Image.new("RGB", (W, H), (4, 5, 8))
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(14 + 10 * (y / H)))
    grad = grad.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (16, 18, 26)), img, grad)

    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
    f_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)
    f_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)

    def neon(base, text, font, cy, core, glow, glow_r=24, tracking=30):
        tmp = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(tmp)
        widths = []
        for ch in text:
            bb = d.textbbox((0, 0), ch, font=font)
            widths.append(bb[2] - bb[0])
        total = sum(widths) + tracking * (len(text) - 1)
        x = (W - total) // 2
        for ch, wch in zip(text, widths):
            d.text((x, cy), ch, font=font, fill=glow)
            x += wch + tracking
        for r in (glow_r, glow_r * 2):
            b = tmp.filter(ImageFilter.GaussianBlur(r))
            base.paste(ImageChops.add(base, b), (0, 0))
        d2 = ImageDraw.Draw(base)
        x = (W - total) // 2
        for ch, wch in zip(text, widths):
            d2.text((x, cy), ch, font=font, fill=core)
            x += wch + tracking

    neon(img, line1, f_big, 700, (235, 240, 245), (90, 200, 255), 22, 26)
    neon(img, line2, f_huge, 1040, (255, 255, 255), (0, 220, 255), 30, 40)
    d = ImageDraw.Draw(img)
    sub = "2026  •  DIRTYGEN  •  СВЯЗИ НЕТ. БАС ЕСТЬ."
    bb = d.textbbox((0, 0), sub, font=f_sm)
    d.text(((W - (bb[2]-bb[0])) // 2, 1700), sub, font=f_sm, fill=(120, 130, 145))
    img.save(path)
    return path

# ============================================================
# zoompan / рендер сегмента
# ============================================================
def zoompan_expr(motion, frames):
    maxz = 1.14
    if motion.endswith("_fast"):
        maxz = 1.22
    cx = "iw/2-(iw/zoom/2)"
    cy = "ih/2-(ih/zoom/2)"
    if motion in ("zin", "zin_fast"):
        rate = (maxz - 1.0) / max(frames - 1, 1)
        return f"z='1+{rate:.6f}*on':x='{cx}':y='{cy}'"
    if motion in ("zout", "zout_fast"):
        rate = (maxz - 1.0) / max(frames - 1, 1)
        return f"z='max({maxz}-{rate:.6f}*on,1.0)':x='{cx}':y='{cy}'"
    if motion == "panLR_fast":
        return f"z='1.16':x='(iw-iw/zoom)*(on/{frames-1})':y='{cy}'"
    if motion == "panLR":
        return f"z='1.10':x='(iw-iw/zoom)*(on/{frames-1})':y='{cy}'"
    if motion == "panRL":
        return f"z='1.10':x='(iw-iw/zoom)*(1-on/{frames-1})':y='{cy}'"
    if motion == "panU":
        return f"z='1.12':x='{cx}':y='(ih-ih/zoom)*(on/{frames-1})'"
    raise ValueError(motion)

def seg_dur_ok(path, expected):
    if not os.path.exists(path):
        return False
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30)
        return abs(float(r.stdout.strip()) - expected) < 0.09
    except Exception:
        return False

def render_segment(cfg, idx):
    sid, dur, frame, motion, extra = cfg["scenes"][idx]
    out = f"{cfg['build']}/{sid}.mp4"
    frames = round(dur * FPS) + 1
    real = (frames - 1) / FPS
    if seg_dur_ok(out, real):
        return
    if motion == "static":
        vf = ("noise=alls=100:allf=t,rgbashift=rh=7:bv=-7,"
              f"drawtext=text='{cfg['ch']}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:"
              "fontsize=54:fontcolor=0x33ff66:x=w-tw-60:y=48:box=1:boxcolor=black@0.35:boxborderw=12,"
              "fade=t=in:st=0:d=0.06,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-f", "lavfi",
               "-i", f"color=c=0x0a0a10:s=1920x1080:d={real:.3f}:r={FPS}",
               "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out]
    elif motion == "title":
        tp = make_title_card(*cfg["title"], cfg["build"])
        zp = zoompan_expr("zin", frames)
        fadeout = round(real - 1.2, 2)
        vf = (f"scale=3840:2160,zoompan={zp}:d={frames}:s=1920x1080:fps={FPS},"
              f"fade=t=out:st={fadeout}:d=1.2,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-i", tp, "-vf", vf,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out]
    else:
        src = f"{F4K}/{frame}.jpg"
        zp = zoompan_expr(motion, frames)
        parts = [f"scale=3840:2160,zoompan={zp}:d={frames}:s=1920x1080:fps={FPS}"]
        if idx == 0:
            parts.append("fade=t=in:st=0:d=1.4")
        if cfg["grade"]:
            parts.append(cfg["grade"])
        if extra:
            parts.append(extra)
        parts.append("format=yuv420p")
        cmd = ["ffmpeg", "-y", "-i", src, "-vf", ",".join(parts),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"[{cfg['build'].split('/')[-1]}] {sid} OK ({real:.2f}s)", flush=True)

# ============================================================
# переходы + финальная сборка
# ============================================================
def trans_dur(cfg, i):
    a, b = cfg["scenes"][i][0], cfg["scenes"][i+1][0]
    if a == "st" or b == "st":
        return 0.12
    if a in cfg["soft"]:
        return 1.20
    if a in cfg["fast"]:
        return 0.30
    return 0.70

def final_assemble(cfg):
    scenes = cfg["scenes"]
    n = len(scenes)
    total = sum(s[1] for s in scenes)
    rend = []
    for i in range(n):
        tprev = trans_dur(cfg, i-1) if i > 0 else 0.0
        tnext = trans_dur(cfg, i) if i < n-1 else 0.0
        rend.append(scenes[i][1] + tprev/2 + tnext/2)
    inputs = []
    for sid, *_ in scenes:
        inputs += ["-i", f"{cfg['build']}/{sid}.mp4"]
    filters = []
    acc = rend[0]
    cur = "[0:v]"
    for i in range(n - 1):
        t = trans_dur(cfg, i)
        acc = acc + rend[i+1] - t
        nxt = f"[v{i+1}]" if i < n-2 else "[vout]"
        filters.append(
            f"{cur}[{i+1}:v]xfade=transition=fade:duration={t:.3f}:offset={acc - rend[i+1]:.3f}{nxt}")
        cur = nxt
    filters.append("[vout]noise=alls=4:allf=t,format=yuv420p[vfinal]")
    fc = ";".join(filters)
    cmd = (["ffmpeg", "-y"] + inputs + ["-i", cfg["audio"],
        "-filter_complex", fc,
        "-map", "[vfinal]", "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-maxrate", "3.0M", "-bufsize", "6.0M",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total:.3f}", "-movflags", "+faststart", cfg["out"]])
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"FINAL OK: {cfg['out']} ({total:.2f}s)", flush=True)

if __name__ == "__main__":
    name, stage = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "render")
    cfg = CONFIGS[name]
    os.makedirs(cfg["build"], exist_ok=True)
    os.makedirs(f"{ROOT}/video", exist_ok=True)
    total = sum(s[1] for s in cfg["scenes"])
    print(f"== {name}: {len(cfg['scenes'])} segments, total {total:.2f}s ==")
    assert abs(total - {"clip1": 185.64, "clip2": 214.03, "clip3": 258.74}[name]) < 0.02, \
        f"total mismatch: {total}"
    if stage == "render":
        for i in range(len(cfg["scenes"])):
            render_segment(cfg, i)
        print(f"ALL {name} SEGMENTS RENDERED")
    else:
        final_assemble(cfg)
