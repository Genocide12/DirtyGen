#!/usr/bin/env python3
"""Сборка клипа «Я не в сети» (Грязный Гена) — 3:07, 1920x1080@30fps.

1. Каждый сегмент рендерится отдельно (zoompan/Ken Burns из 4K кадра)
2. Кроссфейды (xfade) по точной тайм-линии 187.0 c, включая TV-помехи
   («смена канала») перед дропами
3. Финальный проход: зерно плёнки + аудио

Запуск:  python3 build_video.py [render|final]
  render — рендер сегментов (перезапускаемый, пропускает готовые)
  final  — финальная склейка
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = "/home/z/my-project/dirtygen"
F4K = f"{ROOT}/frames_4k"
BUILD = f"{ROOT}/.build"
AUD = f"{ROOT}/audio/soundtrack_placeholder.wav"
OUT = f"{ROOT}/video/ya_ne_v_seti_clip.mp4"
FPS = 30
os.makedirs(BUILD, exist_ok=True)
os.makedirs(f"{ROOT}/video", exist_ok=True)

# ============================================================
# ТАЙМ-ЛАЙН: (id, dur, кадр, движение, доп.фильтры)
# движения: zin / zout / panLR / panRL / panU / *_fast
# ============================================================
SCENES = [
    # ИНТРО 0-20
    ("s01", 7.00, "01", "zin",      ""),
    ("s02", 7.00, "02", "zout",     ""),
    ("s03", 6.00, "03", "zin",      "noise=alls=16:allf=t:enable='between(t,0,0.45)'"),
    # КУПЛЕТ 1: 20-50
    ("s04", 7.00, "04", "panLR",    ""),
    ("s05", 7.00, "05", "zin",      ""),
    ("s06", 8.00, "06", "panRL",    ""),
    ("s07", 8.00, "07", "panU",     ""),
    # ПРЕ-ДРОП 50-60
    ("s08", 5.00, "08", "zin",      ""),
    ("s09", 4.55, "09", "zout",     ""),
    ("st1", 0.45, None, "static",   ""),
    # ДРОП 1: 60-75
    ("s10", 3.50, "10", "zin_fast", "noise=alls=14:allf=t:enable='between(t,0,0.3)'"),
    ("s11", 3.50, "11", "zin_fast", ""),
    ("s12", 4.00, "12", "zout_fast","rgbashift=rh=2:bv=-2"),
    ("s13", 4.00, "13", "panLR_fast","rgbashift=rh=5:bv=-5"),
    # КУПЛЕТ 2: 75-105
    ("s14", 7.00, "14", "zout",     ""),
    ("s15", 7.00, "15", "panU",     ""),
    ("s16", 8.00, "16", "zin",      ""),
    ("s17", 8.00, "17", "panRL",    ""),
    # БРЕЙК 105-120
    ("s18", 7.00, "18", "zin",      "noise=alls=7:allf=t"),
    ("s19", 8.00, "19", "zout",     ""),
    # БИЛД-АП 120-140
    ("s20", 7.00, "20", "panU",     ""),
    ("s21", 7.00, "21", "zin",      ""),
    ("s22", 5.55, "22", "panLR",    ""),
    ("st2", 0.45, None, "static",   ""),
    # ФИНАЛЬНЫЙ ДРОП 140-165
    ("s23", 6.00, "23", "zin_fast", ""),
    ("s24", 6.00, "24", "zout_fast",""),
    ("s25", 6.00, "25", "panLR_fast",""),
    ("s26", 7.00, "26", "zout",     ""),
    # АУТРО 165-187
    ("s27", 8.00, "27", "zin",      ""),
    ("s28", 8.00, "28", "zout",     ""),
    ("ttl", 6.00, None, "title",    ""),
]

def trans_dur(i):
    """Длительность перехода i: SCENES[i] -> SCENES[i+1]."""
    a, b = SCENES[i][0], SCENES[i+1][0]
    if a.startswith("st") or b.startswith("st"):
        return 0.12          # врезка помех — жёсткая
    if a == "s08" or a == "s09":
        return 0.40          # быстрые резки пре-дропа
    if a in ("s10", "s11", "s12"):
        return 0.30          # внутри дропа 1
    if a in ("s23", "s24", "s25"):
        return 0.45          # внутри финального дропа
    if a == "s26" or a == "s19":
        return 1.20          # мягкие крупные смены
    if a == "s28":
        return 1.00          # в титры
    return 0.70              # обычный кроссфейд

# ============================================================
# Карточка титров
# ============================================================
def make_title_card():
    path = f"{BUILD}/title.png"
    if os.path.exists(path):
        return path
    W, H = 3840, 2160
    img = Image.new("RGB", (W, H), (4, 5, 8))
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(14 + 10 * (y / H)))
    grad = grad.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (16, 18, 26)), img, grad)

    f_big  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
    f_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)
    f_sm   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)

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
        blur1 = tmp.filter(ImageFilter.GaussianBlur(glow_r))
        blur2 = tmp.filter(ImageFilter.GaussianBlur(glow_r * 2))
        base.paste(ImageChops.add(base, blur1), (0, 0))
        base.paste(ImageChops.add(base, blur2), (0, 0))
        d2 = ImageDraw.Draw(base)
        x = (W - total) // 2
        for ch, wch in zip(text, widths):
            d2.text((x, cy), ch, font=font, fill=core)
            x += wch + tracking

    neon(img, "ГРЯЗНЫЙ ГЕНА", f_big, 700, (235, 240, 245), (90, 200, 255), 22, 26)
    neon(img, "Я НЕ В СЕТИ",  f_huge, 1040, (255, 255, 255), (0, 220, 255), 30, 40)
    d = ImageDraw.Draw(img)
    sub = "2026  •  DIRTYGEN  •  СВЯЗИ НЕТ. БАС ЕСТЬ."
    bb = d.textbbox((0, 0), sub, font=f_sm)
    d.text(((W - (bb[2]-bb[0])) // 2, 1700), sub, font=f_sm, fill=(120, 130, 145))
    img.save(path)
    print("title card OK")
    return path

# ============================================================
# Рендер одного сегмента
# ============================================================
def zoompan_expr(motion, frames):
    maxz = 1.14
    if motion in ("zin_fast", "zout_fast", "panLR_fast"):
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

def render_segment(idx):
    sid, dur, frame, motion, extra = SCENES[idx]
    out = f"{BUILD}/{sid}.mp4"
    frames = round(dur * FPS) + 1
    if os.path.exists(out):
        return out
    if motion == "static":
        # TV-помехи + зелёный OSD "CH 02" в углу
        vf = ("noise=alls=100:allf=t,rgbashift=rh=7:bv=-7,"
              "drawtext=text='CH 02':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:"
              "fontsize=54:fontcolor=0x33ff66:x=w-tw-60:y=48:box=1:boxcolor=black@0.35:boxborderw=12,"
              "fade=t=in:st=0:d=0.06,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-f", "lavfi",
               "-i", f"color=c=0x0a0a10:s=1920x1080:d={dur}:r={FPS}",
               "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "15", out]
    elif motion == "title":
        tp = make_title_card()
        zp = zoompan_expr("zin", frames)
        fadeout = round(dur - 1.6, 2)
        vf = (f"scale=3840:2160,zoompan={zp}:d={frames}:s=1920x1080:fps={FPS},"
              f"fade=t=out:st={fadeout}:d=1.6,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-i", tp, "-vf", vf,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out]
    else:
        src = f"{F4K}/{frame}.jpg"
        zp = zoompan_expr(motion, frames)
        parts = [f"scale=3840:2160,zoompan={zp}:d={frames}:s=1920x1080:fps={FPS}"]
        if idx == 0:
            parts.append("fade=t=in:st=0:d=1.4")     # старт из черноты
        if extra:
            parts.append(extra)
        parts.append("format=yuv420p")
        vf = ",".join(parts)
        cmd = ["ffmpeg", "-y", "-i", src, "-vf", vf,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"render {sid} OK ({dur}s)", flush=True)
    return out

# ============================================================
# Финальная склейка
# ============================================================
def final_assemble():
    n = len(SCENES)
    rend = []
    for i in range(n):
        tprev = trans_dur(i-1) if i > 0 else 0.0
        tnext = trans_dur(i) if i < n-1 else 0.0
        rend.append(SCENES[i][1] + tprev/2 + tnext/2)
    inputs = []
    for sid, *_ in SCENES:
        inputs += ["-i", f"{BUILD}/{sid}.mp4"]
    filters = []
    acc = rend[0]
    cur = "[0:v]"
    for i in range(n - 1):
        t = trans_dur(i)
        acc = acc + rend[i+1] - t
        nxt = f"[v{i+1}]" if i < n-2 else "[vout]"
        filters.append(
            f"{cur}[{i+1}:v]xfade=transition=fade:duration={t:.3f}:offset={acc - rend[i+1]:.3f}{nxt}"
        )
        cur = nxt
    filters.append("[vout]noise=alls=4:allf=t,format=yuv420p[vfinal]")

    total = sum(s[1] for s in SCENES)
    fc = ";".join(filters)
    cmd = (["ffmpeg", "-y"] + inputs + ["-i", AUD,
        "-filter_complex", fc,
        "-map", "[vfinal]", "-map", f"{n}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-maxrate", "3.0M", "-bufsize", "6.0M",
        "-c:a", "aac", "-b:a", "160k",
        "-t", f"{total:.3f}", "-movflags", "+faststart", OUT])
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"FINAL OK: {OUT} ({total}s)", flush=True)
    # главы для сайта
    chapters = []
    t = 0.0
    marks = {
        "s01": "Интро", "s04": "Куплет 1", "s08": "Пре-дроп", "s10": "Дроп — Смени канал",
        "s14": "Куплет 2", "s18": "Брейк", "s20": "Билд-ап", "s23": "Финальный дроп",
        "s27": "Аутро", "ttl": "Титры",
    }
    for sid, dur, frame, *_ in SCENES:
        if sid in marks:
            chapters.append({"t": round(t, 2), "label": marks[sid], "frame": frame})
        t += dur
    with open(f"{ROOT}/.build/chapters.json", "w") as f:
        json.dump(chapters, f, ensure_ascii=False, indent=1)
    print(json.dumps(chapters, ensure_ascii=False))

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "render"
    if stage == "render":
        for i in range(len(SCENES)):
            render_segment(i)
        print("ALL SEGMENTS RENDERED")
    else:
        final_assemble()
