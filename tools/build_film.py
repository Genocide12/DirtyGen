#!/usr/bin/env python3
"""Сборка клип-фильма «Смени канал» — CH 01, v2: ФИЛЬМ ПО РАСКАДРОВКЕ.

Сценарий = арка трека: тьма (пролог-диалог) -> серая рутина (куплет 1)
-> «тот же город, тот же свет»: ТА ЖЕ УЛИЦА, свет прорывается (dissolve P8->P9)
-> переключение канала на «СМЕНИ КАНАЛ» -> живой неон-мир (aivideo COLOR)
-> «у каждого свой угол» чередование серое/цветное -> гэг с обоями
-> бридж: перекрёсток выбора, шаг в свет -> финал: золото, без капюшона,
-> outro: ТА ЖЕ КРЫША, но рассвет (dissolve P2->P28), титр.

Протагонист: парень в чёрном худи (кадры 02-28 раскадровки).
Материалы: frames_4k/ (28 сцен 4K) + aivideo/ (неон-город) + помехи.
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
F = L.FR4

T = []
def seg(t0, t1, **kw):
    kw["t0"], kw["t1"] = t0, t1
    T.append(kw)

# ================= ПРОЛОГ: диалог в темноте (0-16.5) =================
seg(0.00, 0.40, kind="black", pid="BLK1", dur=0.40)
seg(0.40, 4.00, kind="still", pid="s01", img=F(1), dur=3.60, z1=1.22)          # мегаполис под грозой
seg(4.00, 8.60, kind="still", pid="s02", img=F(2), dur=4.60, z1=1.18)          # он на краю крыши
seg(8.60, 12.20, kind="src", pid="p03x", src=A2, tin=1.00, tout=4.60, grade=G) # серое течение города
seg(12.20, 16.50, kind="still", pid="s03", img=F(3), dur=4.30, z1=1.35)        # лицо + ЭЛТ-помехи

# ================= КУПЛЕТ 1: серая рутина (16.5-46.4) =================
seg(16.50, 20.20, kind="still", pid="s04", img=F(4), dur=3.70, pan="lr")       # толпа на переходе
seg(20.20, 23.90, kind="still", pid="s05", img=F(5), dur=3.70, z1=1.30)        # трамвай, дождь по стеклу
seg(23.90, 27.60, kind="still", pid="s06", img=F(6), dur=3.70, z1=1.28)        # он против потока
seg(27.60, 31.30, kind="src", pid="p07", src=A3, tin=3.20, tout=6.90, grade=G)
seg(31.30, 35.00, kind="src", pid="p08", src=A1, tin=6.00, tout=9.70, grade=G)
seg(35.00, 38.70, kind="still", pid="s07", img=F(7), dur=3.70, z1=1.35, ydrift=0.3)  # один луч света
seg(38.70, 42.40, kind="src", pid="p10", src=A3, tin=6.40, tout=10.10, grade=G)
seg(42.40, 46.40, kind="still", pid="s09", img=F(8), dur=4.00, z1=1.15)        # обычная улица, серо

# ============ «ТОТ ЖЕ ГОРОД. ТОТ ЖЕ СВЕТ.» — сигнатурный кадр ============
seg(46.40, 49.40, kind="dissolve", pid="m89", a=F(8), b=F(9), dur=3.00, crop=1.15)  # свет прорывается
# «Только разных взглядов не счесть» — очередь коротких вспышек
seg(49.40, 50.05, kind="still", pid="s14", img=F(14), dur=0.65, z1=1.20)
seg(50.05, 50.70, kind="still", pid="s15", img=F(15), dur=0.65, z1=1.20)
seg(50.70, 51.35, kind="still", pid="s17", img=F(17), dur=0.65, z1=1.20)
seg(51.35, 52.50, kind="still", pid="s16", img=F(16), dur=1.15, pan="lr")      # диптих: две перспективы

# ================= ПЕРЕКЛЮЧЕНИЕ: «СМЕНИ КАНАЛ» =================
seg(52.50, 52.90, kind="static", pid="ST1", band_y=0.35)
seg(52.90, 53.10, kind="text", pid="TF1", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])

# ================= ДРОП 1: живой канал (53.1-76.6) =================
seg(53.10, 55.50, kind="still", pid="s12", img=F(12), dur=2.40, z1=1.45, osd="CH 02")  # глаз: отражение города
seg(55.50, 61.50, kind="src", pid="p22", src=A2, tin=0.00, tout=3.00, speed=S, grade=C)  # неон-мир (то, что он видит)
seg(61.50, 64.50, kind="still", pid="s13", img=F(13), dur=3.00, z1=1.40,
    extra="rgbashift=rh=-4:bh=4")                                              # сквозь помехи - в неон
seg(64.50, 64.90, kind="static", pid="ST2", band_y=0.62)
seg(64.90, 67.50, kind="src", pid="p25", src=A3, tin=4.00, tout=6.60, grade=C, osd="CH 03")
seg(67.50, 70.50, kind="src", pid="p26", src=A1, tin=3.00, tout=6.00, grade=C)
seg(70.50, 73.50, kind="src", pid="p27", src=A2, tin=4.00, tout=7.00, grade=C)
seg(73.50, 76.60, kind="src", pid="p28", src=A1, tin=7.00, tout=10.10, grade=C,
    extra="zoompan=z='1+0.18*on/93':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30")

# ================= ПРОИГРЫШ: цветной сон (76.6-82.5) =================
seg(76.60, 82.50, kind="src", pid="p29", src=A2, tin=0.00, tout=2.95, speed=S, grade=C)

# ============ КУПЛЕТ 2: серое/цветное чередование (82.5-118.5) ============
seg(82.50, 87.00, kind="src", pid="p30", src=A1, tin=2.00, tout=6.50, grade=G)
seg(87.00, 91.50, kind="src", pid="p31", src=A2, tin=2.00, tout=6.50, grade=C)
seg(91.50, 96.00, kind="src", pid="p32", src=A3, tin=2.00, tout=6.50, grade=G)
seg(96.00, 100.50, kind="src", pid="p33", src=A1, tin=2.00, tout=6.50, grade=C)
seg(100.50, 105.00, kind="src", pid="p34", src=A2, tin=4.00, tout=8.50, grade=G)
seg(105.00, 109.50, kind="src", pid="p35", src=A3, tin=4.00, tout=8.50, grade=C)
seg(109.50, 114.00, kind="src", pid="p36", src=A1, tin=5.00, tout=9.50, grade=G)
seg(114.00, 118.50, kind="src", pid="p37", src=A2, tin=5.79, tout=10.29, grade=C)

# ============ ГЭГ: «Поменял обои на телефоне» (118.5-135.5) ============
seg(118.50, 124.00, kind="still", pid="s18", img=F(18), dur=5.50, z1=1.25)     # диван, усмешка
seg(124.00, 129.50, kind="still", pid="s19", img=F(19), dur=5.50, z0=1.10, z1=1.45)  # обои-закат на экране
seg(129.50, 135.50, kind="src", pid="p40", src=A2, tin=6.00, tout=9.00, speed=S, grade=G)

# ============ БРИДЖ: место выбора (135.5-155.8) ============
BR = "fade=t=in:st=0:d=0.7,fade=t=out:st={OUT}:d=0.7"
seg(135.50, 143.30, kind="src", pid="p41", src=A3, tin=5.00, tout=8.90, speed=S, grade=C,
    extra=BR.format(OUT="7.10"))
seg(143.30, 149.00, kind="still", pid="s21", img=F(21), dur=5.70, pan="lr")    # развилка: тёмная улица -> золотая
seg(149.00, 154.20, kind="src", pid="p43", src=A2, tin=7.60, tout=10.20, speed=S, grade=C,
    extra=BR.format(OUT="4.50"))
seg(154.20, 155.80, kind="still", pid="s22", img=F(22), dur=1.60, z1=1.30)    # шаг из тени в луч

# ============ ФИНАЛЬНЫЙ ПРИПЕВ (155.8-185.6) ============
seg(155.80, 156.50, kind="static", pid="ST3", dur=0.70, band_y=0.80)
seg(156.50, 156.90, kind="static", pid="ST4", band_y=0.20)
seg(156.90, 159.10, kind="src", pid="p47", src=A1, tin=1.00, tout=3.20, grade=C, osd="CH 01")
seg(159.10, 161.70, kind="src", pid="p48", src=A2, tin=3.00, tout=5.60, grade=C)
seg(161.70, 162.35, kind="src", pid="p49a", src=A3, tin=2.00, tout=2.65, grade=G)
seg(162.35, 163.00, kind="src", pid="p49b", src=A3, tin=5.00, tout=5.65, grade=C)
seg(163.00, 163.65, kind="src", pid="p49c", src=A1, tin=8.00, tout=8.65, grade=G)
seg(163.65, 164.30, kind="src", pid="p49d", src=A1, tin=9.35, tout=10.00, grade=C)
seg(164.30, 168.20, kind="src", pid="p50", src=A2, tin=6.00, tout=9.90, grade=C)
seg(168.20, 168.60, kind="static", pid="ST1", band_y=0.35)
seg(168.60, 170.80, kind="still", pid="s23", img=F(23), dur=2.20, z1=1.30)     # ТА ЖЕ улица - в золоте
seg(170.80, 173.40, kind="still", pid="s24", img=F(24), dur=2.60, z1=1.25)     # идёт к камере, без капюшона
seg(173.40, 176.00, kind="src", pid="p54", src=A2, tin=1.00, tout=3.60, grade=C)
seg(176.00, 178.50, kind="still", pid="s26", img=F(26), dur=2.50, z1=1.45, ydrift=0.3)  # бог-лучи

# ============ ФИНАЛ: полный круг (178.5-185.6) ============
seg(178.50, 182.70, kind="dissolve", pid="m228", a=F(2), b=F(28), dur=4.20,
    fades=(0.30, 0.30))   # ТА ЖЕ КРЫША: ночь -> рассвет
seg(182.70, 185.60, kind="still", pid="s25", img=F(25), dur=2.90, z1=1.20, fades=(0.0, 0.60))

# ================= ТИТР =================
seg(185.60, 188.80, kind="text", pid="TITL", dur=3.20, fades=("0.40", "0.40"),
    lines=[("С М Е Н И   К А Н А Л", 108, "(h-th)/2-90", "white"),
           ("ГРЯЗНЫЙ ГЕНА  ·  DIRTYGEN", 30, "(h-th)/2+120", "0xC8C8C8")])

BURSTS = [(52.5, 0.30), (64.5, 0.30), (155.8, 0.34), (168.2, 0.20)]

# ---------- ЗАМЕНЫ НА AI-КАДРЫ (когда откроется квота видео-API) ----------
SUBST = {
    "p03x": ("Q02", 0.00, 3.60),  # диалог: портрет
    "p22":  ("Q07", 0.00, 3.00),  # слоумо-слот (x2 = 6.0): неон-наезд
    "p25":  ("Q08", 0.00, 2.60),  # кран над перекрёстком
    "p26":  ("Q04", 0.00, 3.00),  # тёплое окно кафе в серой улице
    "p27":  ("Q10", 0.00, 3.00),  # аэросъёмка
    "p28":  ("Q11", 0.00, 3.10),  # перекрёсток выбора
    "p29":  ("Q05", 0.00, 2.95),  # слоумо-слот (x2 = 5.9): POV-походка
    "p40":  ("Q03", 0.00, 3.00),  # слоумо-слот (x2 = 6.0): остановка
    "p47":  ("Q09", 0.00, 2.20),  # ракурс к небу
    "p54":  ("Q06", 0.00, 2.60),  # лужа-отражение
}

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
        k = kw["kind"]
        if k == "src":
            need = (kw["tout"] - kw["tin"]) * speed_factor(kw)
            if abs(need - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: источник {need:.2f} != слота {d:.2f}")
            if kw["tout"] > 10.29 + 0.01:
                errs.append(f"#{i} {kw.get('pid')}: tout={kw['tout']} за пределами")
        elif k == "still":
            if abs(kw["dur"] - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: still {kw['dur']:.2f} != {d:.2f}")
        elif k == "dissolve":
            if abs(kw["dur"] - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: dissolve {kw['dur']:.2f} != {d:.2f}")
        elif k in ("static", "black", "text"):
            dur = kw.get("dur", 0.4)
            if abs(dur - d) > 0.06:
                errs.append(f"#{i} {kw.get('pid')}: dur {dur} != {d:.2f}")
    if abs(T[-1]["t1"] - TOTAL) > 0.01:
        errs.append(f"конец {T[-1]['t1']:.2f} != {TOTAL}")
    return errs

# ---------- РЕНДЕР ----------
def render_all():
    import os as _os
    files = []
    for kw in T:
        k = kw["kind"]
        if k == "src":
            src, tin, tout, sfx = kw["src"], kw["tin"], kw["tout"], ""
            sub = SUBST.get(kw["pid"])
            if sub and _os.path.exists(L.GEN(sub[0])) and _os.path.getsize(L.GEN(sub[0])) > 50000:
                src, tin, tout = L.GEN(sub[0]), sub[1], sub[2]
                sfx = "q"
            f = L.render_piece(kw["pid"] + sfx, src, tin, tout,
                               grade=kw.get("grade", ""), speed=kw.get("speed", ""),
                               extra=kw.get("extra", ""), osd=kw.get("osd", ""))
        elif k == "still":
            f = L.render_still(kw["pid"], kw["img"], kw["dur"],
                               z0=kw.get("z0", 1.0), z1=kw.get("z1", 1.25),
                               pan=kw.get("pan", ""), ydrift=kw.get("ydrift", 0.0),
                               extra=kw.get("extra", ""), fades=kw.get("fades", (0.0, 0.0)))
            if kw.get("osd"):
                # OSD поверх готового куска (перезапись с суффиксом)
                f2 = L.piece_path(kw["pid"] + "o")
                if not (_os.path.exists(f2) and _os.path.getsize(f2) > 5000):
                    r = subprocess.run(
                        ["ffmpeg", "-y", "-v", "error", "-i", f, "-an", "-vf",
                         "drawtext=fontfile=" + L.FONTS["mono"] + ":text='" + kw["osd"] +
                         "':x=w-tw-46:y=40:fontsize=34:fontcolor=white@0.85:"
                         "shadowcolor=black@0.6:shadowx=2:shadowy=2",
                         "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                         "-pix_fmt", "yuv420p", "-video_track_timescale", "15360", f2],
                        capture_output=True, text=True)
                    if r.returncode != 0:
                        raise SystemExit(f"osd {kw['pid']} failed")
                f = f2
        elif k == "dissolve":
            f = L.render_dissolve(kw["pid"], kw["a"], kw["b"], kw["dur"],
                                  crop=kw.get("crop", 1.0), fades=kw.get("fades", (0.0, 0.0)))
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
    print(f"таймлайн v2: {len(T)} кусков, {TOTAL}s — проверен, разрывов нет")
    if "--check-only" in sys.argv:
        return
    files = render_all()
    print(f"отрендерено/найдено кусков: {len(files)}")
    lst = os.path.join(BUILD, "film_list.txt")
    with open(lst, "w") as fp:
        for f in files:
            fp.write(f"file '{f}'\n")
    cat = os.path.join(BUILD, "film_cat.mp4")
    if os.path.exists(cat):
        newest = max(os.path.getmtime(f) for f in files)
        if os.path.getmtime(cat) < newest - 2:
            os.remove(cat)
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

def _mtime(p):
    return os.path.getmtime(p) if os.path.exists(p) else 0

if __name__ == "__main__":
    main()
