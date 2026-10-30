#!/usr/bin/env python3
"""Сборка клипа «Смени канал» CH 01 — v4: ФИЛЬМ ПОЛНОСТЬЮ ИЗ 14 AI-КАДРОВ.

Никаких стоп-кадров frames_4k и старых aivideo/01-03: всё видео —
живые AI-сцены Q01-Q14 (aivideo/film/). Арка та же: тьма -> серая рутина
-> «смени канал» -> неон-жизнь -> выбор -> золотой рассвет.

Остались: чёрный пролог, глитч-помехи (static), типографика припевов
(текст ПОВЕРХ живых Q-кадров) и финальный титр.
Запуск: python3 tools/build_film_v4.py [--check-only]
"""
import os, sys, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_lib as L

BUILD = L.BUILD
TOTAL = 188.8
S = L.SLOW2          # слоумо x2: слот = 2 x окно источника
G, C = L.GRAY, L.COLOR
Q = L.GEN            # Q("Q01") -> aivideo/film/Q01.mp4

# фактические длительности Q-клипов (ffprobe, для проверок)
QDUR = {}
for _i in range(1, 15):
    _q = f"Q{_i:02d}"
    _p = Q(_q)
    if not os.path.exists(_p):
        raise SystemExit(f"нет {_p} — v4 собирается только из 14/14")
    _r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "csv=p=0", _p], capture_output=True, text=True)
    QDUR[_q] = float(_r.stdout.strip())

T = []
def seg(t0, t1, kind, pid, **kw):
    kw.update(kind=kind, pid=pid, t0=t0, t1=t1)
    T.append(kw)

def src(t0, t1, pid, q, tin, tout, grade="", slow=False, extra="", osd=""):
    seg(t0, t1, "src", pid, q=q, tin=tin, tout=tout, grade=grade,
        slow=slow, extra=extra, osd=osd)

def typ(t0, t1, pid, q, tin, tout, text, size=100):
    seg(t0, t1, "type", pid, q=q, tin=tin, tout=tout, text=text, size=size)

# ================= ПРОЛОГ: диалог в темноте (0-16.5) =================
seg(0.00, 0.40, "black", "v4blk1", dur=0.40)
src(0.40, 4.60, "v4p01", "Q01", 0.00, 2.10, G, slow=True)          # серый рассвет, он уходит от камеры
src(4.60, 8.60, "v4p02", "Q02", 0.00, 2.00, G, slow=True)          # портрет, пустой взгляд
src(8.60, 12.20, "v4p03", "Q05", 0.00, 1.80, G, slow=True)         # POV-походка, серый асфальт
src(12.20, 16.50, "v4p04", "Q03", 0.00, 2.15, G, slow=True)        # остановка, смотрит на часы

# ================= КУПЛЕТ 1: серая рутина (16.5-46.4) =================
src(16.50, 20.20, "v4p05", "Q01", 2.10, 3.95, G, slow=True)
src(20.20, 23.90, "v4p06", "Q04", 0.00, 1.85, G, slow=True)        # улица, тёплое окно вдали
src(23.90, 27.60, "v4p07", "Q05", 2.00, 3.85, G, slow=True)
src(27.60, 31.30, "v4p08", "Q03", 2.15, 4.00, G, slow=True)
src(31.30, 35.00, "v4p09", "Q04", 2.00, 3.85, G, slow=True)
src(35.00, 38.70, "v4p10", "Q09", 0.00, 1.85, G, slow=True)        # небо между домами: серо -> золото
src(38.70, 42.40, "v4p11", "Q05", 4.00, 5.85, G, slow=True)
src(42.40, 46.40, "v4p12", "Q04", 4.00, 6.00, G, slow=True)

# ============ «ТОТ ЖЕ ГОРОД. ТОТ ЖЕ СВЕТ.» — сигнатурный кадр ============
src(46.40, 49.40, "v4p13", "Q04", 6.00, 9.00, "")                  # тёплое окно кафе, контраст в самом кадре

# «Только разных взглядов не счесть» — очередь живых вспышек
src(49.40, 50.05, "v4f1", "Q07", 0.00, 0.65, C)
src(50.05, 50.70, "v4f2", "Q08", 0.00, 0.65, C)
src(50.70, 51.35, "v4f3", "Q10", 0.00, 0.65, C)
src(51.35, 52.50, "v4f4", "Q06", 0.00, 1.15, "")                   # лужа: серое небо / неон — две перспективы

# ================= ПЕРЕКЛЮЧЕНИЕ: «СМЕНИ КАНАЛ» =================
seg(52.50, 52.90, "static", "v4st1", dur=0.40, band_y=0.35)
seg(52.90, 53.10, "text", "v4tf1", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])

# ================= ДРОП 1: живой канал (53.1-76.6) =================
src(53.10, 55.50, "v4p14", "Q06", 1.15, 2.35, C, slow=True)        # лужа-глаз: отражение города
typ(55.50, 57.10, "v4t1", "Q07", 0.65, 2.25, "ВЗГЛЯНИ ИНАЧЕ")
src(57.10, 58.50, "v4p15", "Q07", 2.25, 3.65, C)
typ(58.50, 60.10, "v4t2", "Q08", 0.65, 2.25, "МИР НЕ ИЗМЕНИЛСЯ")
src(60.10, 61.50, "v4p16", "Q08", 2.25, 3.65, C)
typ(61.50, 63.10, "v4t3", "Q10", 0.65, 2.25, "ТЫ СМОТРИШЬ ИНАЧЕ")
src(63.10, 64.50, "v4p17", "Q10", 2.25, 3.65, C)
seg(64.50, 64.90, "static", "v4st2", dur=0.40, band_y=0.62)
typ(64.90, 66.50, "v4t4", "Q07", 3.65, 5.25, "СМЕНИ КАНАЛ", size=108)
src(66.50, 67.50, "v4p18", "Q08", 3.65, 4.65, C, osd="CH 03")
typ(67.50, 69.10, "v4t5", "Q11", 0.00, 1.60, "НЕ ЖДИ ЗНАКА СВЫШЕ")
src(69.10, 70.50, "v4p19", "Q11", 1.60, 3.00, C)
typ(70.50, 72.10, "v4t6", "Q13", 0.00, 1.60, "ИНОГДА ДОСТАТОЧНО")
src(72.10, 73.50, "v4p20", "Q13", 1.60, 3.00, C)
typ(73.50, 75.10, "v4t7", "Q04", 1.85, 3.45, "СДЕЛАТЬ ШАГ ПОБЛИЖЕ")
src(75.10, 76.60, "v4p21", "Q04", 3.45, 4.95, "",
    extra="zoompan=z='1+0.18*on/45':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30")

# ================= ПРОИГРЫШ: цветной сон (76.6-82.5) =================
src(76.60, 82.50, "v4p22", "Q10", 4.00, 6.95, C, slow=True)        # аэросъёмка золотого часа

# ============ КУПЛЕТ 2: серое/цветное чередование (82.5-118.5) ============
src(82.50, 87.00, "v4p23", "Q05", 5.85, 8.10, G, slow=True)
src(87.00, 91.50, "v4p24", "Q07", 5.25, 7.50, C, slow=True)
src(91.50, 96.00, "v4p25", "Q03", 2.50, 4.75, G, slow=True)
src(96.00, 100.50, "v4p26", "Q08", 5.25, 7.50, C, slow=True)
src(100.50, 105.00, "v4p27", "Q01", 6.00, 8.25, G, slow=True)
src(105.00, 109.50, "v4p28", "Q10", 6.95, 9.20, C, slow=True)
src(109.50, 114.00, "v4p29", "Q02", 2.00, 4.25, G, slow=True)
src(114.00, 118.50, "v4p30", "Q06", 2.35, 4.60, C, slow=True)

# ============ ГЭГ: «Поменял обои на телефоне» (118.5-135.5) ============
src(118.50, 124.00, "v4p31", "Q12", 0.00, 2.75, C, slow=True)      # палец меняет обои на рассвет
src(124.00, 129.50, "v4p32", "Q12", 2.30, 5.05, C, slow=True)      # смотрит, полуулыбка
src(129.50, 135.50, "v4p33", "Q05", 7.00, 10.00, G, slow=True)     # а реальность по-прежнему серая

# ============ БРИДЖ: место выбора (135.5-155.8) ============
src(135.50, 143.30, "v4p34", "Q11", 3.00, 6.90, C, slow=True,
    extra="fade=t=in:st=0:d=0.7,fade=t=out:st=7.10:d=0.7")         # перекрёсток: колеблется -> к свету
src(143.30, 149.00, "v4p35", "Q13", 1.00, 3.85, C, slow=True,
    extra="fade=t=in:st=0:d=0.7,fade=t=out:st=5.00:d=0.7")         # порог света, hesitation
src(149.00, 154.20, "v4p36", "Q11", 7.00, 9.60, C, slow=True,
    extra="fade=t=in:st=0:d=0.7,fade=t=out:st=4.50:d=0.7")         # шаг к свету
src(154.20, 155.80, "v4p37", "Q09", 0.00, 1.60, C)                 # шаг из тени в луч

# ============ ФИНАЛЬНЫЙ ПРИПЕВ (155.8-185.6) ============
seg(155.80, 156.50, "static", "v4st3", dur=0.70, band_y=0.80)
seg(156.50, 156.90, "static", "v4st4", dur=0.40, band_y=0.20)
src(156.90, 159.10, "v4p38", "Q09", 2.00, 4.20, C, osd="CH 01")    # ракурс к небу, золото
typ(159.10, 160.70, "v4t8", "Q07", 5.25, 6.85, "ВЗГЛЯНИ ИНАЧЕ")
src(160.70, 161.70, "v4p39", "Q08", 6.00, 7.00, C)
src(161.70, 162.35, "v4p40", "Q10", 7.00, 7.65, C)                 # цепочка быстрых склеек
src(162.35, 163.00, "v4p41", "Q07", 7.65, 8.30, C)
src(163.00, 163.65, "v4p42", "Q08", 8.30, 8.95, C)
src(163.65, 164.30, "v4p43", "Q10", 9.30, 9.95, C)
src(164.30, 168.20, "v4p44", "Q14", 0.00, 1.95, C, slow=True)      # выход в золотой город, камера вверх
seg(168.20, 168.60, "static", "v4st5", dur=0.40, band_y=0.35)
src(168.60, 170.80, "v4p45", "Q10", 7.90, 10.10, C)                # тот же город — в золоте
typ(170.80, 172.40, "v4t9", "Q13", 4.00, 5.60, "ПУСТЬ МЕНЯЕТСЯ ЗВУК")
src(172.40, 173.40, "v4p46", "Q14", 3.00, 4.00, C)                 # идёт к свету, без капюшона
typ(173.40, 175.00, "v4t10", "Q08", 8.55, 10.15, "ИНОГДА НОВЫЙ ВЗГЛЯД —")
src(175.00, 176.00, "v4p47", "Q08", 4.65, 5.65, C)
typ(176.00, 177.60, "v4t11", "Q11", 8.40, 10.00, "ЭТО ВЫХОД ИЗ КРУГА")
src(177.60, 178.50, "v4p48", "Q09", 4.00, 4.90, C)                 # бог-лучи

# ============ ФИНАЛ: полный круг (178.5-185.6) ============
src(178.50, 182.70, "v4p49", "Q13", 6.00, 8.10, C, slow=True,
    extra="fade=t=in:st=0:d=0.3,fade=t=out:st=3.60:d=0.3")         # порог -> рассвет
src(182.70, 185.60, "v4p50", "Q14", 7.00, 8.45, C, slow=True,
    extra="fade=t=out:st=2.30:d=0.60")                             # рассвет над городом, уход в свет

# ================= ТИТР =================
seg(185.60, 188.80, "text", "v4titl", dur=3.20, fades=("0.40", "0.40"),
    lines=[("С М Е Н И   К А Н А Л", 108, "(h-th)/2-90", "white"),
           ("ГРЯЗНЫЙ ГЕНА  ·  DIRTYGEN", 30, "(h-th)/2+120", "0xC8C8C8")])

BURSTS = [(52.5, 0.30), (64.5, 0.30), (155.8, 0.34), (168.2, 0.20)]

# ---------- ПРОВЕРКИ ----------
def check():
    errs = []
    if abs(T[0]["t0"]) > 1e-6:
        errs.append("таймлайн должен начинаться с 0")
    for i in range(1, len(T)):
        gap = T[i]["t0"] - T[i-1]["t1"]
        if abs(gap) > 0.001:
            errs.append(f"разрыв/наложение #{i}: {T[i-1]['t1']:.2f} -> {T[i]['t0']:.2f}")
    for i, kw in enumerate(T):
        d = kw["t1"] - kw["t0"]
        k = kw["kind"]
        if k == "src":
            w = kw["tout"] - kw["tin"]
            need = w * (2.0 if kw.get("slow") else 1.0)
            if abs(need - d) > 0.06:
                errs.append(f"#{i} {kw['pid']}: источник {need:.2f} != слота {d:.2f}")
            if kw["tout"] > QDUR[kw["q"]] - 0.02:
                errs.append(f"#{i} {kw['pid']}: tout={kw['tout']:.2f} > длит. {QDUR[kw['q']]:.2f}")
        elif k == "type":
            w = kw["tout"] - kw["tin"]
            if abs(w - d) > 0.06:
                errs.append(f"#{i} {kw['pid']}: type {w:.2f} != слота {d:.2f}")
            if kw["tout"] > QDUR[kw["q"]] - 0.02:
                errs.append(f"#{i} {kw['pid']}: tout={kw['tout']:.2f} > длит. {QDUR[kw['q']]:.2f}")
        elif k in ("static", "black", "text"):
            if abs(kw.get("dur", 0.4) - d) > 0.06:
                errs.append(f"#{i} {kw['pid']}: dur {kw.get('dur')} != {d:.2f}")
    if abs(T[-1]["t1"] - TOTAL) > 0.01:
        errs.append(f"конец {T[-1]['t1']:.2f} != {TOTAL}")
    # все 14 кадров должны быть использованы
    used = {kw.get("q") for kw in T if kw["kind"] in ("src", "type")}
    missing = [f"Q{i:02d}" for i in range(1, 15) if f"Q{i:02d}" not in used]
    if missing:
        errs.append(f"не использованы AI-кадры: {', '.join(missing)}")
    return errs

# ---------- РЕНДЕР ----------
def render_all():
    files = []
    for kw in T:
        k = kw["kind"]
        if k == "src":
            f = L.render_piece(kw["pid"], Q(kw["q"]), kw["tin"], kw["tout"],
                               grade=kw.get("grade", ""),
                               speed=S if kw.get("slow") else "",
                               extra=kw.get("extra", ""), osd=kw.get("osd", ""))
        elif k == "type":
            f = L.render_type(kw["pid"], Q(kw["q"]), kw["tin"], kw["tout"],
                              kw["text"], size=kw.get("size", 100))
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
    print(f"таймлайн v4: {len(T)} кусков, {TOTAL}s — проверен, разрывов нет, все 14 AI-кадров в деле")
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

if __name__ == "__main__":
    main()
