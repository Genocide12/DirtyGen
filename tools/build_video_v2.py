#!/usr/bin/env python3
"""Сборка клипа «Я не в сети» v2 — КОРПУС: кадр-точная тайм-линия.

Исправляет баг v1 (видео обрывалось на 54.7с: длительности сегментов
не совпадали с xfade-математикой) и поднимает качество:

  1. Кадр-точная модель: каждый сегмент рендерится ровно на
     dur + t_prev/2 + t_next/2 секунд — переходы центрированы на границах.
  2. Ритм-синхронизация 85 BPM: точки склейки падают на биты саундтрека,
     дропы врубаются ровно на первом 808-ударе (60.35 / 140.40).
  3. Суперсэмплинг: zoompan 4K -> lanczos 1080p (нет лесенок Ken Burns).
  4. Единый цвет-грейд по актам (тьма-холод -> свет-золото) + виньетка.
  5. Типографика поверх ключевых моментов (СМЕНИ КАНАЛ, ВЫБОР, ...).
  6. Глитч-врезки: TV-помехи перед дропами, rgbashift-бёрсты в дропах.
  7. Мастеринг: x264 crf18 slow tune=film, bt709, aac 192k.

Запуск:  python3 build_video_v2.py [render|assemble|master|verify|all]
"""
import json, os, shutil, subprocess, sys, math
from concurrent.futures import ThreadPoolExecutor

ROOT = "/home/z/my-project/dirtygen"
F4K = f"{ROOT}/frames_4k"
BUILD = f"{ROOT}/.build_v2"
AUD = f"{ROOT}/audio/soundtrack_placeholder.wav"
FPS = 30
W, H = 1920, 1080
SS = "3840x2160"          # суперсэмпл zoompan
os.makedirs(BUILD, exist_ok=True)

# ============================================================
# ТАЙМ-ЛАЙН. beat = 60/85 = 0.705882 c (бит саундтрека)
# (sid, start, dur, движение, грейд, fx, оверлей)
#   движение: zin/zout/panLR/panRL/panU (+_fast)
#   оверлей: (png, chain_t_in, chain_t_out, fade_in, fade_out)
# ============================================================
SCENES = [
    # ИНТРО (0-20) — тьма, шёпот
    dict(sid="s01", start=0.000,  dur=7.000, motion="zin",    grade="DARK",
         fx="", ov=("ov_intro.png",   2.80, 7.20, 0.7, 0.7)),
    dict(sid="s02", start=7.000,  dur=7.000, motion="zout",   grade="DARK", fx="", ov=None),
    dict(sid="s03", start=14.000, dur=6.000, motion="zin",    grade="DARK",
         fx="noise=alls=34:allf=t:enable='between(t,0.30,0.62)',"
            "rgbashift=rh=4:bv=-4:enable='between(t,0.30,0.58)'", ov=None),
    # КУПЛЕТ 1 (20-50) — серая рутина, пульс каждые 2 бита
    dict(sid="s04", start=20.000, dur=8.471, motion="panLR",  grade="GREY", fx="", ov=None),
    dict(sid="s05", start=28.471, dur=7.058, motion="zin",    grade="GREY", fx="", ov=None),
    dict(sid="s06", start=35.529, dur=7.059, motion="panRL",  grade="GREY", fx="", ov=None),
    dict(sid="s07", start=42.588, dur=7.412, motion="panU",   grade="GREY", fx="", ov=None),
    # ПРЕ-ДРОП (50-60) — тот же город, тот же свет
    dict(sid="s08", start=50.000, dur=5.000, motion="zin",    grade="GREY",
         fx="", ov=("ov_predrop.png", 51.20, 54.80, 0.6, 0.6)),
    dict(sid="s09", start=55.000, dur=4.750, motion="zout",   grade="WARM1", fx="", ov=None),
    # ДРОП 1 (60.35) — первый 808-удар, жёсткая врезка помех
    dict(sid="st1", start=59.750, dur=0.600, motion="static", grade="", fx="", ov=None),
    dict(sid="s10", start=60.350, dur=3.529, motion="zin_fast",  grade="DROP1",
         fx="rgbashift=rh=6:bv=-6:enable='between(t,0,0.30)'",
         ov=("ov_drop1.png", 60.35, 63.40, 0.10, 0.45)),
    dict(sid="s11", start=63.879, dur=3.530, motion="zout_fast", grade="DROP1",
         fx="rgbashift=rh=4:bv=-4:enable='between(t,0,0.22)'", ov=None),
    dict(sid="s12", start=67.409, dur=4.235, motion="zin_fast",  grade="DROP1",
         fx="rgbashift=rh=4:bv=-4:enable='between(t,0,0.22)'", ov=None),
    dict(sid="s13", start=71.644, dur=3.677, motion="panLR_fast", grade="DROP1",
         fx="rgbashift=rh=5:bv=-5:enable='between(t,0,0.25)'", ov=None),
    # КУПЛЕТ 2 (75.32-105) — разные углы зрения
    dict(sid="s14", start=75.321, dur=8.470, motion="zin",    grade="V2", fx="", ov=None),
    dict(sid="s15", start=83.791, dur=8.471, motion="panU",   grade="V2", fx="", ov=None),
    dict(sid="s16", start=92.262, dur=7.059, motion="panLR",  grade="V2", fx="", ov=None),
    dict(sid="s17", start=99.321, dur=5.679, motion="zout",   grade="V2", fx="", ov=None),
    # БРЕЙК (105-120) — ирония, тиканье
    dict(sid="s18", start=105.000, dur=7.000, motion="zin",   grade="BREAK",
         fx="noise=alls=7:allf=t", ov=None),
    dict(sid="s19", start=112.000, dur=8.000, motion="zout",  grade="BREAK",
         fx="", ov=("ov_break.png", 114.00, 118.50, 0.5, 0.5)),
    # БИЛД-АП (120-140) — потепнение кадр за кадром
    dict(sid="s20", start=120.000, dur=7.059, motion="panU",  grade="WARM1", fx="", ov=None),
    dict(sid="s21", start=127.059, dur=7.059, motion="panLR", grade="WARM2", fx="", ov=None),
    dict(sid="s22", start=134.118, dur=5.682, motion="zin",   grade="WARM3",
         fx="", ov=("ov_choice.png", 137.20, 139.72, 0.5, 0.15)),
    # ФИНАЛЬНЫЙ ДРОП (140.40) — выход из круга
    dict(sid="st2", start=139.800, dur=0.600, motion="static", grade="", fx="", ov=None),
    dict(sid="s23", start=140.400, dur=6.353, motion="zout_fast", grade="FINALE",
         fx="rgbashift=rh=6:bv=-6:enable='between(t,0,0.30)'",
         ov=("ov_drop2.png", 140.40, 143.45, 0.10, 0.45)),
    dict(sid="s24", start=146.753, dur=6.353, motion="zin_fast",  grade="FINALE", fx="", ov=None),
    dict(sid="s25", start=153.106, dur=6.353, motion="panLR_fast", grade="FINALE", fx="", ov=None),
    dict(sid="s26", start=159.459, dur=5.541, motion="zout",   grade="FINALE", fx="", ov=None),
    # АУТРО (165-187) — покой
    dict(sid="s27", start=165.000, dur=8.000, motion="zin",   grade="OUTRO", fx="", ov=None),
    dict(sid="s28", start=173.000, dur=8.000, motion="zout",  grade="OUTRO",
         fx="", ov=("ov_tag.png", 176.50, 180.30, 0.6, 0.6)),
    dict(sid="ttl", start=181.000, dur=6.000, motion="title", grade="", fx="", ov=None),
]

# Оверлей №2 на s23 (вторая строка дропа) — отдельным элементом
OVERLAY2 = dict(sid="s23", png="ov_drop2b.png", t_in=143.50, t_out=146.60, fin=0.4, fout=0.6)

# Переходы: sid -> длительность xfade к СЛЕДУЮЩЕМУ
TRANS = {
    "s01": 0.80, "s02": 0.70, "s03": 0.90,
    "s04": 0.65, "s05": 0.65, "s06": 0.65, "s07": 0.70, "s08": 0.50,
    "s09": 0.06, "st1": 0.06,                      # слэм в помехи и в дроп
    "s10": 0.28, "s11": 0.28, "s12": 0.28, "s13": 0.70,
    "s14": 0.65, "s15": 0.65, "s16": 0.65, "s17": 1.00, "s18": 0.70,
    "s19": 0.80, "s20": 0.65, "s21": 0.50,
    "s22": 0.06, "st2": 0.06,                      # слэм в финальный дроп
    "s23": 0.35, "s24": 0.35, "s25": 0.35, "s26": 1.20,
    "s27": 0.90, "s28": 1.20,
}

GRADES = {
    "DARK":   "eq=contrast=1.04:saturation=0.94,colorbalance=bs=0.05:bm=0.02:bh=-0.02,vignette=angle=PI/4.7",
    "GREY":   "eq=contrast=1.03:saturation=0.90,colorbalance=bs=0.04:bm=0.01,vignette=angle=PI/4.7",
    "WARM1":  "eq=contrast=1.05:saturation=1.05,colorbalance=bs=0.02:rm=0.02,vignette=angle=PI/4.7",
    "DROP1":  "eq=contrast=1.10:saturation=1.15,colorbalance=bs=0.06:rs=-0.03:rm=0.02,vignette=angle=PI/4.2",
    "V2":     "eq=contrast=1.05:saturation=1.00,colorbalance=bs=0.03,vignette=angle=PI/4.7",
    "BREAK":  "eq=contrast=1.02:saturation=0.88,vignette=angle=PI/4.6",
    "WARM2":  "eq=contrast=1.05:saturation=1.07,colorbalance=rm=0.04:bm=-0.02,vignette=angle=PI/4.7",
    "WARM3":  "eq=contrast=1.06:saturation=1.11,colorbalance=rm=0.05:bh=0.02,vignette=angle=PI/4.6",
    "FINALE": "eq=contrast=1.06:saturation=1.18,colorbalance=rm=0.05:gm=0.02:bh=0.02,vignette=angle=PI/4.7",
    "OUTRO":  "eq=contrast=1.02:saturation=1.08,colorbalance=rm=0.03:gm=0.01,vignette=angle=PI/4.8",
}

N = len(SCENES)

def timeline():
    """Возвращает списки: file_dur, frames, S (начало файла в цепи), offsets."""
    fd, S, off = [0.0]*N, [0.0]*N, [0.0]*(N-1)
    for i, sc in enumerate(SCENES):
        tin = TRANS[SCENES[i-1]["sid"]] / 2 if i > 0 else 0.0
        tout = TRANS[sc["sid"]] / 2 if i < N-1 else 0.0
        fd[i] = tin + sc["dur"] + tout
        S[i] = sc["start"] - tin
    for i in range(N-1):
        off[i] = SCENES[i+1]["start"] - TRANS[SCENES[i]["sid"]] / 2
    frames = [round(d * FPS) + 2 for d in fd]     # +2 кадра безопасности
    total = S[-1] + fd[-1]
    return fd, frames, S, off, total

def zoompan(motion, frames):
    mz = 1.14
    if motion.endswith("_fast"):
        mz = 1.24
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    n = max(frames - 1, 1)
    if motion in ("zin", "zin_fast"):
        r = (mz - 1.0) / n
        return f"z='1+{r:.7f}*on':x='{cx}':y='{cy}'"
    if motion in ("zout", "zout_fast"):
        r = (mz - 1.0) / n
        return f"z='max({mz}-{r:.7f}*on,1.0)':x='{cx}':y='{cy}'"
    if motion == "panLR_fast":
        return f"z='1.18':x='(iw-iw/zoom)*(on/{n})':y='{cy}'"
    if motion == "panLR":
        return f"z='1.10':x='(iw-iw/zoom)*(on/{n})':y='{cy}'"
    if motion == "panRL":
        return f"z='1.10':x='(iw-iw/zoom)*(1-on/{n})':y='{cy}'"
    if motion == "panU":
        return f"z='1.12':x='{cx}':y='(ih-ih/zoom)*(on/{n})'"
    raise ValueError(motion)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"CMD FAILED: {' '.join(cmd[:8])}...\n{r.stderr[-2500:]}")

# ============================================================
# ТИПОГРАФИКА (PNG 1920x1080 RGBA, неон, кириллица)
# ============================================================
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def _layer(W_, H_):
    return Image.new("RGBA", (W_, H_), (0, 0, 0, 0))

def neon_text(base, text, font, cx_, cy_, core, glow, r=18, tracking=0,
              chroma=None):
    """Неон-текст с glow; chroma=(цвет,±сдвиг) — хроматический дубль."""
    tmp = _layer(*base.size)
    d = ImageDraw.Draw(tmp)
    widths = []
    for ch in text:
        bb = d.textbbox((0, 0), ch, font=font)
        widths.append(bb[2] - bb[0])
    total = sum(widths) + tracking * (len(text) - 1)
    x0 = cx_ - total / 2
    if chroma:
        ccol, dx = chroma
        ct = _layer(*base.size)
        dc = ImageDraw.Draw(ct)
        x = x0 + dx
        for ch, wch in zip(text, widths):
            dc.text((x, cy_), ch, font=font, fill=ccol)
            x += wch + tracking
        base.alpha_composite(ct.filter(ImageFilter.GaussianBlur(3)))
    x = x0
    for ch, wch in zip(text, widths):
        d.text((x, cy_), ch, font=font, fill=glow)
        x += wch + tracking
    base.alpha_composite(tmp.filter(ImageFilter.GaussianBlur(r)))
    base.alpha_composite(tmp.filter(ImageFilter.GaussianBlur(r * 2)))
    d2 = ImageDraw.Draw(base)
    x = x0
    for ch, wch in zip(text, widths):
        d2.text((x, cy_), ch, font=font, fill=core + (255,))
        x += wch + tracking
    return base

def text_width(text, font, tracking=0):
    tmp = _layer(10, 10)
    d = ImageDraw.Draw(tmp)
    w = 0
    for ch in text:
        bb = d.textbbox((0, 0), ch, font=font)
        w += bb[2] - bb[0] + tracking
    return w

def make_cards():
    """Все текстовые карточки."""
    out = {}

    # 1) Интро-титры (низ, слева-по-центру): артист + трек
    im = _layer(W, H)
    f1 = ImageFont.truetype(FB, 46)
    f2 = ImageFont.truetype(FB, 88)
    neon_text(im, "ГРЯЗНЫЙ ГЕНА", f1, W/2, H-232, (225, 232, 240), (60, 170, 255), 12, 18)
    neon_text(im, "Я НЕ В СЕТИ",  f2, W/2, H-160, (255, 255, 255), (0, 200, 255), 16, 10)
    out["ov_intro.png"] = im

    # 2) Пре-дроп: строка песни
    im = _layer(W, H)
    f = ImageFont.truetype(FB, 64)
    neon_text(im, "ТОТ ЖЕ ГОРОД. ТОТ ЖЕ СВЕТ.", f, W/2, H/2-40,
              (240, 240, 245), (255, 170, 60), 14, 8)
    out["ov_predrop.png"] = im

    # 3) Дроп 1: СМЕНИ КАНАЛ — хроматический глитч-неон
    im = _layer(W, H)
    f = ImageFont.truetype(FB, 168)
    neon_text(im, "СМЕНИ КАНАЛ", f, W/2, H/2-110, (255, 255, 255),
              (0, 220, 255), 22, 14, chroma=((255, 0, 140, 200), -8))
    im2 = _layer(W, H)
    f2_ = ImageFont.truetype(FB, 54)
    neon_text(im2, "ВЗГЛЯНИ ИНАЧЕ", f2_, W/2, H/2+96, (235, 240, 250), (255, 0, 140), 12, 22)
    out["ov_drop1.png"] = Image.alpha_composite(im, im2)

    # 4) Брейк: ироничная реплика
    im = _layer(W, H)
    f = ImageFont.truetype(FR, 52)
    d = ImageDraw.Draw(im)
    t = "— Поменял обои на телефоне."
    bb = d.textbbox((0, 0), t, font=f)
    tw = bb[2] - bb[0]
    d.text(((W - tw) / 2, H - 200), t, font=f, fill=(235, 235, 240, 255))
    out["ov_break.png"] = im

    # 5) Билд-ап: ВЫБОР
    im = _layer(W, H)
    f = ImageFont.truetype(FB, 190)
    neon_text(im, "ВЫБОР", f, W/2, H/2-120, (255, 252, 244), (255, 190, 70), 26, 22,
              chroma=((255, 120, 40, 160), 6))
    out["ov_choice.png"] = im

    # 6) Финальный дроп: СМЕНИ КАНАЛ + вторая строка
    im = _layer(W, H)
    f = ImageFont.truetype(FB, 168)
    neon_text(im, "СМЕНИ КАНАЛ", f, W/2, H/2-110, (255, 255, 255),
              (255, 200, 90), 22, 14, chroma=((255, 60, 0, 200), -8))
    out["ov_drop2.png"] = im

    im = _layer(W, H)
    f = ImageFont.truetype(FB, 58)
    neon_text(im, "МИР НЕ ИЗМЕНИЛСЯ — ТЫ СМОТРИШЬ ИНАЧЕ", f, W/2, H/2+40,
              (250, 248, 242), (255, 190, 80), 13, 6)
    out["ov_drop2b.png"] = im

    # 7) Аутро-теглайн
    im = _layer(W, H)
    f = ImageFont.truetype(FB, 72)
    neon_text(im, "СВЯЗИ НЕТ. БАС ЕСТЬ.", f, W/2, H/2-46, (245, 246, 250), (0, 220, 255), 16, 12)
    out["ov_tag.png"] = im

    for name, img in out.items():
        img.save(f"{BUILD}/{name}")
        print("card", name)
    return out

def make_title_card():
    """Финальная карточка: ГРЯЗНЫЙ ГЕНА / Я НЕ В СЕТИ (4K)."""
    path = f"{BUILD}/title.png"
    if os.path.exists(path):
        return path
    TW, TH = 3840, 2160
    img = Image.new("RGB", (TW, TH), (4, 5, 8))
    grad = Image.new("L", (1, TH))
    for y in range(TH):
        grad.putpixel((0, y), int(14 + 10 * (y / TH)))
    grad = grad.resize((TW, TH))
    img = Image.composite(Image.new("RGB", (TW, TH), (16, 18, 26)), img, grad)
    f_big = ImageFont.truetype(FB, 200)
    f_huge = ImageFont.truetype(FB, 300)
    f_sm = ImageFont.truetype(FR, 72)
    tmp = Image.new("RGB", (TW, TH), (0, 0, 0))
    d = ImageDraw.Draw(tmp)
    def widths(text, font, tr):
        ws = []
        for ch in text:
            bb = d.textbbox((0, 0), ch, font=font)
            ws.append(bb[2] - bb[0])
        return ws, sum(ws) + tr * (len(text) - 1)
    def neon(text, font, cy, core, glow, gr, tr):
        ws, total = widths(text, font, tr)
        x = (TW - total) // 2
        for ch, wch in zip(text, ws):
            d.text((x, cy), ch, font=font, fill=glow)
            x += wch + tr
        b1 = tmp.filter(ImageFilter.GaussianBlur(gr))
        b2 = tmp.filter(ImageFilter.GaussianBlur(gr * 2))
        nonlocal img
        img = ImageChops.add(img, b1)
        img = ImageChops.add(img, b2)
        d2 = ImageDraw.Draw(img)
        x = (TW - total) // 2
        for ch, wch in zip(text, ws):
            d2.text((x, cy), ch, font=font, fill=core)
            x += wch + tr
        tmp.paste(0, (0, 0, TW, TH))
    neon("ГРЯЗНЫЙ ГЕНА", f_big, 700, (235, 240, 245), (90, 200, 255), 22, 26)
    neon("Я НЕ В СЕТИ", f_huge, 1040, (255, 255, 255), (0, 220, 255), 30, 40)
    d3 = ImageDraw.Draw(img)
    sub = "2026  •  DIRTYGEN  •  СВЯЗИ НЕТ. БАС ЕСТЬ."
    bb = d3.textbbox((0, 0), sub, font=f_sm)
    d3.text(((TW - (bb[2] - bb[0])) // 2, 1700), sub, font=f_sm, fill=(120, 130, 145))
    img.save(path)
    print("title card OK")
    return path

# ============================================================
# РЕНДЕР СЕГМЕНТОВ (параллельно 2 потока)
# ============================================================
# лёгкий кодек для промежуточных сегментов (экономия RAM в контейнере)
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "13",
       "-x264-params", "rc-lookahead=20:refs=2:bframes=2"]

def _frames_ok(path, expected):
    """Цел ли файл и сколько в нём кадров (None = битый)."""
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        return None
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-count_frames", "-show_entries", "stream=nb_read_frames",
                         "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return int(pr.stdout.strip())
    except ValueError:
        return None

def render_segment(i):
    sc = SCENES[i]
    fd, frames, S, off, _ = timeline()
    fr, sdur = frames[i], fd[i]
    out = f"{BUILD}/{sc['sid']}.mp4"
    got = _frames_ok(out, fr)
    if got is not None and abs(got - fr) <= 2:
        return out                     # уже готов и цел
    if os.path.exists(out):
        os.remove(out)                 # битый/неправильный — перерендерить
    m = sc["motion"]
    if m == "static":
        vf = ("noise=alls=100:allf=t,rgbashift=rh=7:bv=-7,"
              "drawtext=text='CH 02':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:"
              "fontsize=54:fontcolor=0x33ff66:x=w-tw-60:y=48:box=1:boxcolor=black@0.35:boxborderw=12,"
              "eq=brightness=-0.04,format=yuv420p,setsar=1")
        cmd = ["ffmpeg", "-y", "-f", "lavfi",
               "-i", f"color=c=0x0a0a10:s={W}x{H}:d={sdur + 0.2}:r={FPS}",
               "-vf", vf, "-frames:v", str(fr)] + ENC + [out]
    elif m == "title":
        tp = make_title_card()
        zp = zoompan("zin", fr)
        fout = round(sc["dur"] - 1.6, 2)
        vf = (f"scale=3840:2160,zoompan={zp}:d={fr}:s={SS}:fps={FPS},"
              f"scale={W}:{H}:flags=lanczos,"
              f"fade=t=out:st={fout}:d=1.6,format=yuv420p,setsar=1")
        cmd = ["ffmpeg", "-y", "-i", tp, "-vf", vf, "-frames:v", str(fr)] + ENC + [out]
    else:
        src = f"{F4K}/{int(sc['sid'][1:]):02d}.jpg"
        zp = zoompan(m, fr)
        parts = [f"scale=3840:2160,zoompan={zp}:d={fr}:s={SS}:fps={FPS}",
                 f"scale={W}:{H}:flags=lanczos"]
        if i == 0:
            parts.append("fade=t=in:st=0:d=1.4")       # старт из черноты
        if sc["grade"]:
            parts.append(GRADES[sc["grade"]])
        if sc["fx"]:
            parts.append(sc["fx"])
        # оверлей-типографика: нормализуем спеки к кортежам
        ov = sc["ov"]
        extra = OVERLAY2 if sc["sid"] == OVERLAY2["sid"] else None
        specs = []
        if ov:
            specs.append((ov[0], ov[1], ov[2], ov[3], ov[4]))
        if extra:
            specs.append((extra["png"], extra["t_in"], extra["t_out"],
                          extra["fin"], extra["fout"]))
        if specs:
            k = len(specs)
            segs = [f"[0:v]{','.join(parts)}[bg]"]
            for j, (png, t_in, t_out, fi, fo) in enumerate(specs, start=1):
                li = t_in - S[i]
                lo = max(t_out - S[i] - fo, li + 0.05)
                segs.append(
                    f"[{j}:v]format=rgba,fade=t=in:st={li:.2f}:d={fi}:alpha=1,"
                    f"fade=t=out:st={lo:.2f}:d={fo}:alpha=1[ov{j}]")
            prev = "[bg]"
            for j in range(1, k + 1):
                if j == k:
                    segs.append(f"{prev}[ov{j}]overlay=0:0:shortest=0")  # открытый выход
                else:
                    segs.append(f"{prev}[ov{j}]overlay=0:0:shortest=0[m{j}]")
                    prev = f"[m{j}]"
            graph = ";".join(segs) + ",format=yuv420p,setsar=1"
            inputs = ["-i", src]
            for png, *_ in specs:
                inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{sdur + 1:.2f}",
                           "-i", f"{BUILD}/{png}"]
            cmd = (["ffmpeg", "-y"] + inputs +
                   ["-filter_complex", graph, "-frames:v", str(fr)] + ENC + [out])
        else:
            parts.append("format=yuv420p,setsar=1")
            cmd = ["ffmpeg", "-y", "-i", src, "-vf", ",".join(parts),
                   "-frames:v", str(fr)] + ENC + [out]
    run(cmd)
    # проверка длительности
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-count_frames", "-show_entries", "stream=nb_read_frames",
                         "-of", "csv=p=0", out], capture_output=True, text=True)
    got = int(pr.stdout.strip() or 0)
    if abs(got - fr) > 2:
        raise RuntimeError(f"{sc['sid']}: frames {got} != {fr}")
    print(f"render {sc['sid']} OK  ({fr}f, {sdur:.2f}s+pad)", flush=True)
    return out

def render_all():
    make_cards()
    # ПОСЛЕДОВАТЕЛЬНО: 2 параллельных 4K-ffmpeg не лезут в RAM контейнера (3GB)
    for i in range(N):
        sc = SCENES[i]
        if not os.path.exists(f"{BUILD}/{sc['sid']}.mp4"):
            print(f"render {sc['sid']} start...", flush=True)
        render_segment(i)
    print("ALL SEGMENTS RENDERED")

# ============================================================
# СБОРКА: xfade-цепь (кадр-точная) -> промежуточный мастер
# ============================================================
def assemble():
    fd, frames, S, off, total = timeline()
    # --- самопроверка модели ---
    assert abs((S[-1] + fd[-1]) - total) < 1e-6
    assert abs(total - 187.0) < 0.2, f"total {total} != 187"
    for i in range(N - 1):
        t = TRANS[SCENES[i]["sid"]]
        chain_end = S[i] + fd[i]
        assert off[i] + 1e-6 >= S[i], f"offset {i} до начала"
        assert off[i] + t <= chain_end + 0.05, \
            f"xface {i}: offset+t {off[i]+t:.3f} > файл {chain_end:.3f}"
    print(f"model OK: total={total:.3f}s, сегментов={N}")

    inputs = []
    for sc in SCENES:
        inputs += ["-i", f"{BUILD}/{sc['sid']}.mp4"]
    filters = []
    cur = "[0:v]"
    for i in range(N - 1):
        t = TRANS[SCENES[i]["sid"]]
        nxt = f"[v{i+1}]"
        filters.append(
            f"{cur}[{i+1}:v]xfade=transition=fade:duration={t:.3f}:"
            f"offset={off[i]:.3f}{nxt}")
        cur = nxt
    filters.append(f"{cur}format=yuv420p,setsar=1[vout]")
    fc = ";".join(filters)
    out = f"{BUILD}/assemble.mkv"
    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "12",
            "-r", str(FPS), out])
    run(cmd)
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    print(f"ASSEMBLE OK: {out} ({dur:.2f}s)")
    return out

# ============================================================
# МАСТЕР: зерно + кодек + аудио + faststart
# ============================================================
def master(audio=AUD, out=f"{ROOT}/video/ya_ne_v_seti_clip.mp4"):
    src = f"{BUILD}/assemble.mkv"
    cmd = (["ffmpeg", "-y", "-i", src, "-i", audio,
            "-filter_complex",
            "[0:v]noise=alls=3:allf=t,format=yuv420p,setsar=1[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "film",
            "-profile:v", "high", "-level", "4.0",
            "-x264-params", "ref=4:bframes=4",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv",
            "-c:a", "aac", "-b:a", "192k",
            "-t", "187.0", "-movflags", "+faststart", out])
    run(cmd)
    print(f"MASTER OK: {out}")
    return out

def web_version(src=f"{ROOT}/video/ya_ne_v_seti_clip.mp4"):
    out = f"{ROOT}/video/ya_ne_v_seti_clip_web.mp4"
    cmd = (["ffmpeg", "-y", "-i", src,
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-maxrate", "3.2M", "-bufsize", "6.4M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", out])
    run(cmd)
    print(f"WEB OK: {out}")
    return out

# ============================================================
# ВЕРИФИКАЦИЯ: кадры, длительность, спот-чек, аудио
# ============================================================
def verify():
    ok = True
    for path in (f"{ROOT}/video/ya_ne_v_seti_clip.mp4",):
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
             "-show_entries", "stream=nb_read_frames,duration,width,height,r_frame_rate",
             "-of", "json", path], capture_output=True, text=True)
        st = json.loads(pr.stdout)["streams"][0]
        nfr = int(st["nb_read_frames"])
        dur = float(st["duration"])
        exp = 187 * FPS
        print(f"{path}: {nfr} кадров (ожид ~{exp}), {dur:.2f}s, "
              f"{st['width']}x{st['height']}@{st['r_frame_rate']}")
        if abs(nfr - exp) > 4 or abs(dur - 187.0) > 0.3:
            ok = False
        pa = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=duration,channels,sample_rate",
             "-of", "json", path], capture_output=True, text=True)
        aud = json.loads(pa.stdout)["streams"][0]
        print(f"  аудио: {float(aud['duration']):.2f}s "
              f"{aud['sample_rate']}Hz x{aud['channels']}")
        if abs(float(aud["duration"]) - 187.0) > 0.5:
            ok = False
    # спот-чек кадров в ключевые моменты
    spots = [3, 10, 25, 55, 60.5, 62, 70, 90, 110, 116, 130, 138.5,
             140.5, 150, 170, 184]
    os.makedirs(f"{BUILD}/spot", exist_ok=True)
    for t in spots:
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i",
             f"{ROOT}/video/ya_ne_v_seti_clip.mp4", "-frames:v", "1",
             f"{BUILD}/spot/f{t:05.1f}.jpg"], capture_output=True)
        if r.returncode != 0:
            ok = False
            print("SPOT FAIL at", t)
    print("SPOT frames:", ", ".join(str(s) for s in spots))
    print("VERIFY:", "PASS" if ok else "FAIL")
    return ok

def chapters():
    """Главы для сайта: (время, метка, кадр-превью)."""
    marks = [
        (0.0, "Интро", "01"), (20.0, "Куплет 1", "04"), (50.0, "Пре-дроп", "08"),
        (60.35, "Дроп — Смени канал", "10"), (75.32, "Куплет 2", "14"),
        (105.0, "Брейк", "18"), (120.0, "Билд-ап", "20"),
        (140.4, "Финальный дроп", "23"), (165.0, "Аутро", "27"),
        (181.0, "Титры", None),
    ]
    ch = [{"t": t, "label": lb, "frame": fr} for t, lb, fr in marks]
    with open(f"{ROOT}/.build/chapters.json", "w") as f:
        json.dump(ch, f, ensure_ascii=False, indent=1)
    print(json.dumps(ch, ensure_ascii=False))

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "render":
        render_all()
    elif stage == "assemble":
        assemble()
    elif stage == "master":
        a = sys.argv[2] if len(sys.argv) > 2 else AUD
        master(a)
    elif stage == "web":
        web_version()
    elif stage == "verify":
        verify()
    elif stage == "chapters":
        chapters()
    else:
        render_all()
        assemble()
        master()
        web_version()
        verify()
        chapters()

