#!/usr/bin/env python3
"""Библиотека сборки клип-фильма «Смени канал» (ch1).

Идея фильма = идея трека: «МИР НЕ ИЗМЕНИЛСЯ — ТЫ СМОТРИШЬ ИНАЧЕ».
Один и тот же материал в двух «каналах»: СЕРОМ (обесцвеченный, холодный)
и ЖИВОМ (неон, тепло). Переключение — вспышка ТВ-помех на словах
«СМЕНИ КАНАЛ».

Куски (pieces) рендерятся с одинаковыми параметрами кодирования,
затем склеиваются concat -c copy. Каждый кусок: 1920x1080, 30 fps CFR,
yuv420p, timebase 1/15360.
"""
import os, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(BASE, ".build_film")
PIECES = os.path.join(BUILD, "pieces")
os.makedirs(PIECES, exist_ok=True)

TRACK = "/home/z/my-project/upload/Трек .mp3"

# ---- кодирование кусков: одинаковое у всех (для concat -c copy) ----
X264 = ["-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
        "-preset", "medium", "-crf", "18", "-maxrate", "4M", "-bufsize", "8M",
        "-pix_fmt", "yuv420p", "-g", "60", "-keyint_min", "6",
        "-r", "30", "-fps_mode", "cfr", "-video_track_timescale", "15360"]

FONTS = {
    "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}
_unb = os.path.join(BUILD, "Unbounded-Black.ttf")
if os.path.exists(_unb):
    FONTS["title"] = _unb
else:
    FONTS["title"] = FONTS["bold"]

AIV = {i: os.path.join(BASE, "aivideo", f"0{i}.mp4") for i in (1, 2, 3)}
GEN = lambda q: os.path.join(BASE, "aivideo", "film", f"{q}.mp4")

# ---- грейды ----
# СЕРЫЙ канал: монохром. Хрома убивается В КОНЦЕ цепочки (после зерна),
# иначе colorbalance/noise возвращают цвет (~+14 сат. на тёмных кадрах).
GRAY = ("eq=saturation=0:contrast=0.94:brightness=-0.03,"
        "vignette=0.5,noise=alls=6:allf=t,eq=saturation=0")
# ЖИВОЙ канал: неон вперёд
COLOR = ("eq=saturation=1.35:contrast=1.10:gamma=1.02,"
         "colorbalance=rs=0.03:bs=-0.05:rm=0.04:bm=-0.04:rh=0.05:bh=-0.05,"
         "unsharp=5:5:0.6,noise=alls=4:allf=t")

SLOW2 = "tblend=all_mode=average,framestep=2,setpts=2*PTS"


def _esc(s):
    return s.replace("\\", "").replace("'", "").replace(":", "\\:")


def piece_path(pid):
    return os.path.join(PIECES, pid + ".mp4")


def render_piece(pid, src, tin, tout, grade="", speed="", extra="", osd=""):
    """Кусок из источника: fps30 → trim → грейд → слоумо → доп.фильтры."""
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    chain = ["fps=30", "settb=AVTB", f"trim=start={tin}:end={tout}",
             "setpts=PTS-STARTPTS"]
    if grade:
        chain.append(grade)
    if speed:
        chain.append(speed)
    if extra:
        chain.append(extra)
    if osd:
        chain.append(
            f"drawtext=fontfile={FONTS['mono']}:text='{_esc(osd)}':"
            "x=w-tw-46:y=40:fontsize=34:fontcolor=white@0.85:"
            "shadowcolor=black@0.6:shadowx=2:shadowy=2")
    chain.append("format=yuv420p")
    vf = ",".join(chain)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-an", "-vf", vf] + X264 + [out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr)
        raise SystemExit(f"piece {pid} failed")
    return out


def render_static(pid, dur=0.4, band_y=0.5, band_h=14):
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    vf = (f"nullsrc=s=1920x1080:r=30:d={dur},"
          "noise=alls=100:allf=t+u,eq=contrast=1.35,"
          f"drawbox=x=0:y=ih*{band_y}:w=iw:h={band_h}:color=white@0.55:t=fill,"
          "format=yuv420p")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", vf,
                        "-an"] + X264 + [out], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr)
        raise SystemExit(f"static {pid} failed")
    return out


def render_black(pid, dur):
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                        "-i", f"color=black:s=1920x1080:r=30:d={dur}",
                        "-an"] + X264 + [out], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"black {pid} failed")
    return out


def render_text(pid, dur, lines, fades=("0.35", "0.35"), bg="black"):
    """Титульный кусок: чёрный фон, строки (text,size,y,color)."""
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    vf = [f"color={bg}:s=1920x1080:r=30:d={dur}"]
    for text, size, y, color in lines:
        vf.append(
            f"drawtext=fontfile={FONTS['title']}:text='{_esc(text)}':"
            f"x=(w-tw)/2:y={y}:fontsize={size}:fontcolor={color}"
            + (":shadowcolor=black@0.5:shadowx=3:shadowy=3" if bg == "black" else ""))
    fi, fo = fades
    if float(fi) > 0:
        vf.append(f"fade=t=in:st=0:d={fi}")
    if float(fo) > 0:
        vf.append(f"fade=t=out:st={max(0.0, dur - float(fo)):.3f}:d={fo}")
    vf.append("format=yuv420p")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                        "-i", ",".join(vf), "-an"] + X264 + [out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr)
        raise SystemExit(f"text {pid} failed")
    return out


def render_audio(out_wav, bursts):
    """Трек + шипение помех в моменты bursts=[(t, vol)] → wav 48k."""
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        return out_wav
    n = 1 + len(bursts)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", TRACK]
    fc = []
    for k, (t, vol) in enumerate(bursts, start=1):
        cmd += ["-f", "lavfi", "-t", "0.35",
                "-i", "anoisesrc=color=white:sample_rate=48000:amplitude=0.7"]
    cmd += ["-filter_complex"]
    parts = []
    parts.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[a0]")
    for k, (t, vol) in enumerate(bursts, start=1):
        ms = int(t * 1000)
        parts.append(
            f"[{k}:a]volume={vol},highpass=f=240,lowpass=f=7000,"
            f"afade=t=out:st=0.12:d=0.23,adelay={ms}|{ms}[a{k}]")
    ins = "".join(f"[a{i}]" for i in range(n))
    parts.append(
        ins + f"amix=inputs={n}:duration=first:normalize=0,"
              "afade=t=out:st=185.1:d=0.5[amix]")
    cmd += [";".join(parts), "-map", "[amix]", "-c:a", "pcm_s16le", "-ar", "48000", out_wav]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], file=sys.stderr)
        raise SystemExit("audio mix failed")
    return out_wav


# ======================================================================
#  v2: СТОП-КАДРЫ (4K раскадровка, 28 сцен) + МОРФЫ
# ======================================================================
STILL_GRADE = ("eq=contrast=1.05:saturation=1.06,"
               "noise=alls=5:allf=t")

FR4 = lambda n: os.path.join(BASE, "frames_4k", f"{n:02d}.jpg")


def render_still(pid, img, dur, z0=1.0, z1=1.25, pan="", ydrift=0.0,
                 extra="", fades=(0.0, 0.0)):
    """Кусок из стоп-кадра 4K: наезд/панорама (zoompan), зерно.
    pan: '' центр, 'lr' слева направо, 'rl' справа налево.
    ydrift>0: камера всплывает (для кадров 'вверх к свету').
    """
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    T = max(2, round(dur * 30))
    if pan in ("lr", "rl"):
        z = max(z0, z1, 1.25)
        if pan == "lr":
            x = f"(iw-iw/zoom)*on/{T}"
        else:
            x = f"(iw-iw/zoom)*(1-on/{T})"
        y = "ih/2-(ih/zoom/2)"
    else:
        z = 0
        x = "iw/2-(iw/zoom/2)"
        if ydrift > 0:
            y = f"(ih-ih/zoom)*(0.5-{ydrift}*on/{T})"
        else:
            y = "ih/2-(ih/zoom/2)"
    if pan:
        zexpr = f"{z:.4f}"
    else:
        zexpr = f"{z0:.4f}+({z1:.4f}-{z0:.4f})*on/{T}"
    chain = [
        "scale=3840:2160",
        f"zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s=1920x1080:fps=30",
        STILL_GRADE,
    ]
    if extra:
        chain.append(extra)
    fi, fo = fades
    if fi > 0:
        chain.append(f"fade=t=in:st=0:d={fi}")
    if fo > 0:
        chain.append(f"fade=t=out:st={max(0.0, dur - fo):.3f}:d={fo}")
    chain.append("format=yuv420p")
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", img,
           "-an", "-vf", ",".join(chain), "-frames:v", str(T)] + X264 + [out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], file=sys.stderr)
        raise SystemExit(f"still {pid} failed")
    return out


def render_dissolve(pid, imgA, imgB, dur, crop=1.0, fades=(0.0, 0.0)):
    """Длинный dissolve A->B (xfade) с одинаковым кропом обоих кадров.
    Город не движется - меняется свет. crop=1.15 - продолжение наезда
    предыдущего куска (бесшовный стык). Работает в реальном времени."""
    out = piece_path(pid)
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        return out
    cw = round(3840 / crop / 2) * 2
    ch = round(2160 / crop / 2) * 2
    pre = ("scale=3840:2160,"
           f"crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})/2,"
           "scale=1920:1080,fps=30,settb=AVTB,setsar=1")
    fc = (f"[0:v]{pre}[a];[1:v]{pre}[b];"
          f"[a][b]xfade=transition=fade:duration={dur:.3f}:offset=0,"
          + STILL_GRADE)
    fi, fo = fades
    tail = []
    if fi > 0:
        tail.append(f"fade=t=in:st=0:d={fi}")
    if fo > 0:
        tail.append(f"fade=t=out:st={max(0.0, dur - fo):.3f}:d={fo}")
    tail.append("format=yuv420p")
    fc += "," + ",".join(tail) + "[v]"
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", imgA,
           "-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", imgB,
           "-filter_complex", fc, "-map", "[v]", "-an",
           "-frames:v", str(round(dur * 30))] + X264 + [out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], file=sys.stderr)
        raise SystemExit(f"dissolve {pid} failed")
    return out
