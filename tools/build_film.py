#!/usr/bin/env python3
"""Сборка клип-фильма «Смени канал» — CH 01 (v1: aivideo-монтаж).

Фильм по смыслу трека: «Мир не изменился — ты смотришь иначе».
Один и тот же город в двух каналах: СЕРОМ и ЖИВОМ (неон).
Переключение каналов = вспышка помех на «СМЕНИ КАНАЛ».

Тайминг привязан к строкам трека (из синхро-текста исходного сайта).
Запуск: python3 tools/build_film.py [--check-only]
"""
import os, sys, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_lib as L

BUILD = L.BUILD
TOTAL = 188.8

S = L.SLOW2
G, C = L.GRAY, L.COLOR
A1, A2, A3 = L.AIV[1], L.AIV[2], L.AIV[3]

# ---------- ТАЙМЛАЙН ----------
# kind: src | static | black | text
#       src: {src, tin, tout, grade, speed, extra, osd}
T = []
def seg(t0, t1, **kw):
    kw["t0"], kw["t1"] = t0, t1
    T.append(kw)

# --- Пролог: диалог (0-16.5) — серый канал, сонное течение ---
seg(0.00, 0.40, kind="black", pid="BLK1", dur=0.40)
seg(0.40, 8.60, kind="src", pid="p02", src=A1, tin=0.00, tout=4.10, speed=S, grade=G)
seg(8.60, 16.50, kind="src", pid="p03", src=A2, tin=0.00, tout=3.95, speed=S, grade=G)

# --- Куплет 1 (16.5-46.4): серая рутина, смена планов по строкам ---
seg(16.50, 20.20, kind="src", pid="p04", src=A3, tin=0.00, tout=3.70, grade=G)
seg(20.20, 23.90, kind="src", pid="p05", src=A1, tin=3.00, tout=6.70, grade=G)
seg(23.90, 27.60, kind="src", pid="p06", src=A2, tin=0.00, tout=3.70, grade=G)
seg(27.60, 31.30, kind="src", pid="p07", src=A3, tin=3.20, tout=6.90, grade=G)
seg(31.30, 35.00, kind="src", pid="p08", src=A1, tin=6.00, tout=9.70, grade=G)
seg(35.00, 38.70, kind="src", pid="p09", src=A2, tin=3.00, tout=6.70, grade=G)
seg(38.70, 42.40, kind="src", pid="p10", src=A3, tin=6.40, tout=10.10, grade=G)
seg(42.40, 46.40, kind="src", pid="p11", src=A1, tin=0.00, tout=2.00, speed=S, grade=G)

# --- Подход к припеву: «Тот же город. Тот же свет.» ---
seg(46.40, 47.90, kind="src", pid="p12", src=A2, tin=0.00, tout=1.50, grade=G)
seg(47.90, 49.40, kind="src", pid="p13", src=A3, tin=0.00, tout=1.50, grade=G)
# «Только разных взглядов не счесть» — очередь коротких вспышек
seg(49.40, 50.05, kind="src", pid="p14", src=A1, tin=0.00, tout=0.65, grade=G)
seg(50.05, 50.70, kind="src", pid="p15", src=A2, tin=1.50, tout=2.15, grade=G)
seg(50.70, 51.35, kind="src", pid="p16", src=A3, tin=3.00, tout=3.65, grade=G)
seg(51.35, 52.00, kind="src", pid="p17", src=A1, tin=5.00, tout=5.65, grade=G)
seg(52.00, 52.50, kind="src", pid="p18", src=A2, tin=7.00, tout=7.50, grade=G)

# --- «СМЕНИ КАНАЛ.» — ПЕРЕКЛЮЧЕНИЕ: помехи + вспышка титула ---
seg(52.50, 52.90, kind="static", pid="ST1", band_y=0.35)
seg(52.90, 53.10, kind="text", pid="TF1", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])
# Тот же кадр, что открывал фильм — но теперь живой. МИР НЕ ИЗМЕНИЛСЯ.
seg(53.10, 55.50, kind="src", pid="p21", src=A1, tin=0.00, tout=2.40, grade=C, osd="CH 02")
seg(55.50, 61.50, kind="src", pid="p22", src=A2, tin=0.00, tout=3.00, speed=S, grade=C)
seg(61.50, 64.50, kind="src", pid="p23", src=A3, tin=0.00, tout=3.00, grade=C)

# --- Второе переключение ---
seg(64.50, 64.90, kind="static", pid="ST2", band_y=0.62)
seg(64.90, 67.50, kind="src", pid="p25", src=A3, tin=4.00, tout=6.60, grade=C, osd="CH 03")
seg(67.50, 70.50, kind="src", pid="p26", src=A1, tin=3.00, tout=6.00, grade=C)
seg(70.50, 73.50, kind="src", pid="p27", src=A2, tin=4.00, tout=7.00, grade=C)
# «Сделать шаг поближе» — наезд камеры
seg(73.50, 76.60, kind="src", pid="p28", src=A1, tin=7.00, tout=10.10, grade=C,
    extra="zoompan=z='1+0.18*on/93':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30")

# --- Проигрыш (76.6-82.5): цветной сон ---
seg(76.60, 82.50, kind="src", pid="p29", src=A2, tin=0.00, tout=2.95, speed=S, grade=C)

# --- Куплет 2 (82.5-118.5): серое ↔ цветное — «у каждого свой угол» ---
seg(82.50, 87.00, kind="src", pid="p30", src=A1, tin=2.00, tout=6.50, grade=G)
seg(87.00, 91.50, kind="src", pid="p31", src=A2, tin=2.00, tout=6.50, grade=C)
seg(91.50, 96.00, kind="src", pid="p32", src=A3, tin=2.00, tout=6.50, grade=G)
seg(96.00, 100.50, kind="src", pid="p33", src=A1, tin=2.00, tout=6.50, grade=C)
seg(100.50, 105.00, kind="src", pid="p34", src=A2, tin=4.00, tout=8.50, grade=G)
seg(105.00, 109.50, kind="src", pid="p35", src=A3, tin=4.00, tout=8.50, grade=C)
seg(109.50, 114.00, kind="src", pid="p36", src=A1, tin=5.00, tout=9.50, grade=G)
seg(114.00, 118.50, kind="src", pid="p37", src=A2, tin=5.79, tout=10.29, grade=C)

# --- Диалог-шутка (118.5-135.5): «Поменял обои на телефоне» ---
seg(118.50, 124.00, kind="src", pid="p38", src=A3, tin=4.00, tout=6.75, speed=S, grade=C)
seg(124.00, 129.50, kind="src", pid="p39", src=A1, tin=0.00, tout=2.75, speed=S, grade=C)
seg(129.50, 135.50, kind="src", pid="p40", src=A2, tin=6.00, tout=9.00, speed=S, grade=G)

# --- Бридж (135.5-156.5): «место выбора» — дышащие кроссфейды ---
BR = "fade=t=in:st=0:d=0.7,fade=t=out:st={OUT}:d=0.7"
seg(135.50, 143.30, kind="src", pid="p41", src=A3, tin=5.00, tout=8.90, speed=S, grade=C,
    extra=BR.format(OUT="7.10"))
seg(143.30, 149.00, kind="src", pid="p42", src=A1, tin=7.00, tout=9.85, speed=S, grade=C,
    extra=BR.format(OUT="5.00"))
seg(149.00, 154.20, kind="src", pid="p43", src=A2, tin=7.60, tout=10.20, speed=S, grade=C,
    extra=BR.format(OUT="4.50"))
seg(154.20, 155.80, kind="src", pid="p44", src=A3, tin=0.00, tout=1.60, grade=C)

# --- Помехи «NO SIGNAL» → финальный припев ---
seg(155.80, 156.50, kind="static", pid="ST3", dur=0.70, band_y=0.80)
seg(156.50, 156.90, kind="static", pid="ST4", band_y=0.20)
seg(156.90, 159.10, kind="src", pid="p47", src=A1, tin=1.00, tout=3.20, grade=C, osd="CH 01")
seg(159.10, 161.70, kind="src", pid="p48", src=A2, tin=3.00, tout=5.60, grade=C)
# «МИР НЕ ИЗМЕНИЛСЯ» — строб серое/цветное (одними и теми же кадрами)
seg(161.70, 162.35, kind="src", pid="p49a", src=A3, tin=2.00, tout=2.65, grade=G)
seg(162.35, 163.00, kind="src", pid="p49b", src=A3, tin=5.00, tout=5.65, grade=C)
seg(163.00, 163.65, kind="src", pid="p49c", src=A1, tin=8.00, tout=8.65, grade=G)
seg(163.65, 164.30, kind="src", pid="p49d", src=A1, tin=9.35, tout=10.00, grade=C)
seg(164.30, 168.20, kind="src", pid="p50", src=A2, tin=6.00, tout=9.90, grade=C)
seg(168.20, 168.60, kind="static", pid="ST1", band_y=0.35)  # повтор ST1
seg(168.60, 170.80, kind="src", pid="p52", src=A3, tin=6.00, tout=8.20, grade=C)
seg(170.80, 173.40, kind="src", pid="p53", src=A1, tin=4.00, tout=6.60, grade=C)
seg(173.40, 176.00, kind="src", pid="p54", src=A2, tin=1.00, tout=3.60, grade=C)
seg(176.00, 178.50, kind="src", pid="p55", src=A3, tin=8.75, tout=10.00, speed=S, grade=C)

# --- Финал (178.5-185.6): выдох, темп уходит ---
seg(178.50, 182.70, kind="src", pid="p56", src=A1, tin=6.00, tout=8.10, speed=S, grade=C)
seg(182.70, 185.60, kind="src", pid="p57", src=A2, tin=8.84, tout=10.29, speed=S, grade=C,
    extra="fade=t=out:st=2.30:d=0.60")

# --- Титр ---
seg(185.60, 188.80, kind="text", pid="TITL", dur=3.20, fades=("0.40", "0.40"),
    lines=[("С М Е Н И   К А Н А Л", 108, "(h-th)/2-90", "white"),
           ("ГРЯЗНЫЙ ГЕНА  ·  DIRTYGEN", 30, "(h-th)/2+120", "0xC8C8C8")])

BURSTS = [(52.5, 0.30), (64.5, 0.30), (155.8, 0.34), (168.2, 0.20)]

# ---------- ПРОВЕРКИ ----------
def speed_factor(kw):
    return 2.0 if kw.get("speed") else 1.0

def check():
    errs = []
    if abs(T[0]["t0"]) > 1e-6:
        errs.append("таймлайн должен начинаться с 0")
    for i in range(1, len(T)):
        gap = T[i]["t0"] - T[i-1]["t1"]
        if abs(gap) > 0.001:
            errs.append(f"разрыв/наложение #{i}: {T[i-1]['t1']:.2f} → {T[i]['t0']:.2f}")
    for i, kw in enumerate(T):
        d = kw["t1"] - kw["t0"]
        if kw["kind"] == "src":
            need = (kw["tout"] - kw["tin"]) * speed_factor(kw)
            if abs(need - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: длительность куска {need:.2f} != слота {d:.2f}")
            if kw["tout"] > 10.29 + 0.01:
                errs.append(f"#{i} {kw.get('pid')}: tout={kw['tout']} за пределами клипа")
        elif kw["kind"] in ("static", "black", "text"):
            dur = kw.get("dur", 0.4)
            if abs(dur - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: dur {dur} != {d:.2f}")
    if abs(T[-1]["t1"] - TOTAL) > 0.01:
        errs.append(f"конец {T[-1]['t1']:.2f} != {TOTAL}")
    return errs

# ---------- РЕНДЕР ----------
def render_all():
    files = []
    for kw in T:
        k = kw["kind"]
        if k == "src":
            f = L.render_piece(kw["pid"], kw["src"], kw["tin"], kw["tout"],
                               grade=kw.get("grade", ""), speed=kw.get("speed", ""),
                               extra=kw.get("extra", ""), osd=kw.get("osd", ""))
        elif k == "static":
            f = L.render_static(kw["pid"], dur=kw.get("dur", 0.4), band_y=kw.get("band_y", 0.5))
        elif k == "black":
            f = L.render_black(kw["pid"], kw["dur"])
        elif k == "text":
            f = L.render_text(kw["pid"], kw["dur"], kw["lines"], kw.get("fades", ("0.35", "0.35")))
        files.append(f)
    return files

def main():
    errs = check()
    if errs:
        print("ОШИБКИ ТАЙМЛАЙНА:")
        [print(" -", e) for e in errs]
        raise SystemExit(1)
    print(f"таймлайн: {len(T)} кусков, {TOTAL}s — проверен, разрывов нет")
    if "--check-only" in sys.argv:
        return
    files = render_all()
    print(f"отрендерено/найдено кусков: {len(files)}")
    lst = os.path.join(BUILD, "film_list.txt")
    with open(lst, "w") as fp:
        for f in files:
            fp.write(f"file '{f}'\n")
    cat = os.path.join(BUILD, "film_cat.mp4")
    if not (os.path.exists(cat) and os.path.getsize(cat) > 1000000):
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                            "-i", lst, "-c", "copy", cat], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1200:], file=sys.stderr); raise SystemExit("concat fail")
    aud = L.render_audio(os.path.join(BUILD, "audio_final.wav"), BURSTS)
    out = os.path.join(BUILD, "ch1_film.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cat, "-i", aud,
                        "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", out], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr); raise SystemExit("mux fail")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,size", "-of", "json", out],
                       capture_output=True, text=True)
    j = json.loads(p.stdout)["format"]
    print(f"ГОТОВО: {out}  {float(j['size'])/1e6:.1f} MB  {j['duration']}s")

if __name__ == "__main__":
    main()
