#!/usr/bin/env python3
"""Сборка клипа CH 02 «Смени канал» (v5, план Б) — по режиссёрскому монтажному
листу юзера (03:34 / 214с), полностью из 25 AI-кадров S01-S25.

Монтажный лист: 7 актов, 14 сцен. Арка: холодный нуар старого канала ->
дуализм двух взглядов -> первый всплеск (войд экранов) -> ирония ->
внутренний переход (глитчи -> искры -> зеркальный туннель) -> финальный дроп
(крыша, золото, рассвет) -> интимный аутро и уход в свет.

Тайминг сцен — в точности по листу режиссёра (сумма = 214с):
  Сц1 0-15 | Сц2 15-30 | Сц3 30-45 | Сц4 45-65 | Сц5 65-80 | Сц6 80-110 |
  Сц7 110-125 | Сц8 125-135 | Сц9 135-145 | Сц10 145-160 | Сц11 160-175 |
  Сц12 175-195 | Сц13 195-205 | Сц14 205-214 | титр 214-217.3.
Дроп 82с попадает на Сц6 (вой экранов) после вспышки «СМЕНИ КАНАЛ»,
световой взрыв 160с — на вход Сц11 (крыша).

Переходы по листу: soft dissolve 30с, match cut 45с, whitescreen flash 80с,
резкая склейка 110с, glitch-to-black 135с, прямая 145с, световой взрыв 160с,
dissolve 205с, fade to black к 214с.

Запуск: python3 tools/build_film_ch2.py [--check-only]
(--check-only при отсутствии кадров считает их длительность 10.0с)
"""
import os, sys, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_lib as L

BUILD = L.BUILD
TOTAL = 217.300
TRACK2 = "/home/z/my-project/upload/Трек2.mp3"
S = L.SLOW2
ASSUME = "--check-only" in sys.argv

# ---- актовые грейды (7 актов монтажного листа) ----
# АКТ 1 «Старый канал»: глубокий сине-серый, холодный нуар, плотный дождь.
COLD = ("eq=saturation=0.20:contrast=1.10:brightness=-0.05,"
        "vignette=0.52,noise=alls=7:allf=t,"
        "eq=saturation=0.15,colorbalance=bs=0.06:bm=0.04:bh=0.02")
# АКТ 2 «Два взгляда»: тёплая сторона дуализма — луч, детали, надежда.
WARM2 = ("eq=saturation=1.25:contrast=1.08:gamma=1.02,"
         "colorbalance=rs=0.05:rm=0.04:rh=0.06:bs=-0.03:bh=-0.02,"
         "unsharp=5:5:0.5,noise=alls=4:allf=t")
# АКТ 3 «Первый всплеск»: тёмный войд, серебро, высокий контраст.
SILVER = ("eq=saturation=0.55:contrast=1.24:gamma=0.97:brightness=-0.03,"
          "colorbalance=bs=0.04:rs=0.02:rh=0.05:bh=-0.02,"
          "unsharp=5:5:0.8,noise=alls=5:allf=t")
# АКТ 4 «Ирония»: приглушённые тона, плоская фронтальная композиция.
MUTED = ("eq=saturation=0.55:contrast=0.94:gamma=1.03:brightness=0.01,"
         "colorbalance=rs=0.02:gs=0.01:rm=0.02,noise=alls=4:allf=t")
# АКТ 5 «Внутренний переход»: разгон, бетон -> зеркало + тепло.
RISE = ("eq=saturation=1.10:contrast=1.10,"
        "colorbalance=rs=0.03:rm=0.03:rh=0.04:bs=-0.02,"
        "unsharp=5:5:0.6,noise=alls=5:allf=t")
# АКТ 6 «На высоте»: максимальный масштаб, яркое золото, рассвет.
GOLD = ("eq=saturation=1.35:contrast=1.15:gamma=1.02:brightness=0.02,"
        "colorbalance=rs=0.06:rm=0.05:rh=0.08:gs=0.01:bs=-0.04:bh=-0.03,"
        "unsharp=5:5:0.7,noise=alls=4:allf=t")
# АКТ 7 «Аутро»: интимная камера, тёплое угасание.
WARM = ("eq=saturation=0.92:contrast=1.02:gamma=1.04,"
        "colorbalance=rs=0.04:rm=0.03:rh=0.05,noise=alls=3:allf=t")

GEN = lambda n: os.path.join(L.BASE, "aivideo", "film_ch2", f"{n}.mp4")

# фактические длительности S-кадров (ffprobe, для проверок)
QDUR = {}
for _name in [f"S{i:02d}" for i in range(1, 26)]:
    _p = GEN(_name)
    if not os.path.exists(_p):
        if ASSUME:
            QDUR[_name] = 10.0
            continue
        raise SystemExit(f"нет {_p} — v5 (план Б) собирается только из 25/25")
    _r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "csv=p=0", _p], capture_output=True, text=True)
    QDUR[_name] = float(_r.stdout.strip())

T = []
def seg(t0, t1, kind, pid, **kw):
    kw.update(kind=kind, pid=pid, t0=t0, t1=t1)
    T.append(kw)

def src(t0, t1, pid, q, tin, tout, grade="", slow=False, extra="", osd=""):
    seg(t0, t1, "src", pid, q=q, tin=tin, tout=tout, grade=grade,
        slow=slow, extra=extra, osd=osd)

def typ(t0, t1, pid, q, tin, tout, text, size=100):
    seg(t0, t1, "type", pid, q=q, tin=tin, tout=tout, text=text, size=size)

# ================= 0-0.4: чёрный вход =================
seg(0.00, 0.40, "black", "v6blk1", dur=0.40)

# ================= АКТ 1 · СТАРЫЙ КАНАЛ (0-45): COLD =================
src(0.40, 8.00, "v6p01", "S01", 0.00, 3.80, COLD, slow=True)    # Сц1: толпа в motion blur
src(8.00, 15.00, "v6p02", "S02", 0.00, 3.50, COLD, slow=True)    # Сц1: dolly zoom отъезд
src(15.00, 22.00, "v6p03", "S03", 0.00, 3.50, COLD, slow=True)   # Сц2: метро, лицо в стекле
src(22.00, 30.00, "v6p04", "S04", 0.00, 4.00, COLD, slow=True,   # Сц2: скроллинг+тоннель
    extra="fade=t=out:st=7.3:d=0.7")                              # -> soft dissolve на 30
src(30.00, 37.60, "v6p05", "S05", 0.00, 3.80, COLD, slow=True)   # Сц3: лифт, взгляд наружу
src(37.60, 45.00, "v6p06", "S06", 0.00, 3.70, COLD, slow=True)   # Сц3: телефоны, tilt-up

# ================= АКТ 2 · ДВА ВЗГЛЯДА (45-80) =================
src(45.00, 55.00, "v6p07", "S07", 0.00, 5.00, COLD, slow=True)   # Сц4: тёмная сторона улицы
src(55.00, 62.00, "v6p08", "S08", 0.00, 3.50, WARM2, slow=True)  # Сц4: тёплое отражение, pan
typ(62.00, 65.00, "v6t1", "S08", 3.50, 6.50, "ВЗГЛЯНИ ИНАЧЕ")     # Сц4/5: хук над живым кадром
src(65.00, 72.00, "v6p09", "S09", 0.00, 3.50, WARM2, slow=True)  # Сц5: макро капля
typ(72.00, 74.00, "v6t2", "S10", 0.00, 2.00, "МИР НЕ ИЗМЕНИЛСЯ")  # Сц5: «реальность та же»
typ(74.00, 76.00, "v6t3", "S10", 2.00, 4.00, "ТЫ СМОТРИШЬ ИНАЧЕ") # Сц5: «изменился фокус»
src(76.00, 79.60, "v6p10", "S10", 4.00, 5.80, WARM2, slow=True)  # Сц5: rack focus на лицо

# переход по листу: whitescreen flash на нарастании -> «СМЕНИ КАНАЛ» -> ДРОП 82
seg(79.60, 79.80, "static", "v6st1", dur=0.20, band_y=0.35)
seg(79.80, 80.00, "text", "v6fl1", dur=0.20, fades=("0", "0"), bg="white",
    lines=[])
seg(80.00, 80.20, "text", "v6tf1", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])
seg(80.20, 82.00, "black", "v6blk2", dur=1.80)

# ================= АКТ 3 · ПЕРВЫЙ ВСПЛЕСК (82-110): SILVER =================
src(82.00, 90.00, "v6p11", "S11", 0.00, 4.00, SILVER, slow=True)  # Сц6: войд парящих экранов
typ(90.00, 92.00, "v6t4", "S11", 4.00, 6.00, "НЕ ЖДИ ЗНАКА СВЫШЕ")
src(92.00, 100.00, "v6p12", "S12", 0.00, 4.00, SILVER, slow=True) # Сц6: подход+касание
src(100.00, 110.00, "v6p13", "S13", 0.00, 5.00, SILVER, slow=True)  # Сц6: разлёт осколков, 180°

# ================= АКТ 4 · ИРОНИЯ (110-135): MUTED =================
src(110.00, 117.00, "v6p14", "S14", 0.00, 3.50, MUTED, slow=True)  # Сц7: гордые обои
typ(117.00, 119.00, "v6t5", "S14", 3.50, 5.50, "ИНОГДА ДОСТАТОЧНО")
src(119.00, 125.00, "v6p15", "S15", 0.00, 3.00, MUTED, slow=True)  # Сц7: серая комната, абсурд
src(125.00, 133.00, "v6p16", "S16", 0.00, 4.00, MUTED, slow=True)  # Сц8: ироничная полуулыбка
typ(133.00, 134.60, "v6t6", "S16", 4.00, 5.60, "СДЕЛАТЬ ШАГ ПОБЛИЖЕ")
# переход по листу: glitch-to-black fade
seg(134.60, 135.00, "static", "v6st2", dur=0.40, band_y=0.62)
seg(135.00, 135.60, "black", "v6blk3", dur=0.60)

# ================= АКТ 5 · ВНУТРЕННИЙ ПЕРЕХОД (135.6-160): RISE =================
src(135.60, 141.60, "v6p17", "S17", 0.00, 3.00, RISE, slow=True)   # Сц9: глитчи -> искры
typ(141.60, 143.60, "v6t7", "S17", 3.00, 5.00, "ПУСТЬ МЕНЯЕТСЯ ЗВУК")
src(143.60, 145.00, "v6p18", "S17", 5.00, 5.70, RISE, slow=True)  # Сц9: искры гаснут
src(145.00, 152.00, "v6p19", "S18", 0.00, 3.50, RISE, slow=True)   # Сц10: тёмный переход, tracking
typ(152.00, 154.00, "v6t8", "S19", 0.00, 2.00, "ИНОГДА НОВЫЙ ВЗГЛЯД —")
src(154.00, 159.60, "v6p20", "S19", 2.00, 4.80, RISE, slow=True)  # Сц10: стены -> зеркала, выход
# переход по листу: световой взрыв (белый/золотой) на вход Сц11
seg(159.60, 160.00, "static", "v6st3", dur=0.40, band_y=0.80)
seg(160.00, 160.20, "text", "v6fl2", dur=0.20, fades=("0", "0"), bg="white",
    lines=[])

# ================= АКТ 6 · НА ВЫСОТЕ (160.2-195): GOLD =================
src(160.20, 167.00, "v6p21", "S20", 0.00, 3.40, GOLD, slow=True,  # Сц11: выход на крышу
    extra="fade=t=in:st=0:d=0.35")                                 # взрыв света из вспышки
typ(167.00, 169.00, "v6t9", "S21", 0.00, 2.00, "ЭТО ВЫХОД ИЗ КРУГА")
src(169.00, 175.00, "v6p22", "S21", 2.00, 5.00, GOLD, slow=True)  # Сц11: облет 360°
src(175.00, 185.00, "v6p23", "S22", 0.00, 5.00, GOLD, slow=True)  # Сц12: аэро, свет по фасадам
src(185.00, 195.00, "v6p24", "S23", 0.00, 5.00, GOLD, slow=True)  # Сц12: FPV push-in к герою

# ================= АКТ 7 · АУТРО (195-214): WARM =================
src(195.00, 205.00, "v6p25", "S24", 0.00, 5.00, WARM, slow=True)  # Сц13: выдох, улыбка (тишина трека 196-198 внутри)
src(205.00, 213.20, "v6p26", "S25", 0.00, 4.10, WARM, slow=True,  # Сц14: уход в свет, камера вниз
    extra="fade=t=out:st=7.2:d=1.0")                              # -> глубокое затемнение к 214
seg(213.20, 214.00, "black", "v6blk4", dur=0.80)                   # «ровно на 03:34» — чёрный

# ================= ТИТР (214-217.3) =================
seg(214.00, 217.30, "text", "v6titl", dur=3.30, fades=("0.40", "0.40"),
    lines=[("С М Е Н И   К А Н А Л", 108, "(h-th)/2-90", "white"),
           ("ГРЯЗНЫЙ ГЕНА  ·  DIRTYGEN  ·  CH 02", 30, "(h-th)/2+120", "0xC8C8C8")])

# помехи (аудио-шипение + визуальный static) в моменты переходов по листу
BURSTS = [(79.6, 0.30), (134.6, 0.30), (159.6, 0.34)]

def qpath(q):
    return GEN(q)

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
    used = {kw.get("q") for kw in T if kw["kind"] in ("src", "type")}
    missing = [n for n in QDUR if n not in used]
    if missing:
        errs.append(f"не использованы AI-кадры: {', '.join(missing)}")
    return errs

# ---------- РЕНДЕР ----------
def render_all():
    files = []
    for kw in T:
        k = kw["kind"]
        if k == "src":
            f = L.render_piece(kw["pid"], qpath(kw["q"]), kw["tin"], kw["tout"],
                               grade=kw.get("grade", ""),
                               speed=S if kw.get("slow") else "",
                               extra=kw.get("extra", ""), osd=kw.get("osd", ""))
        elif k == "type":
            f = L.render_type(kw["pid"], qpath(kw["q"]), kw["tin"], kw["tout"],
                              kw["text"], size=kw.get("size", 100))
        elif k == "static":
            f = L.render_static(kw["pid"], dur=kw.get("dur", 0.4), band_y=kw.get("band_y", 0.5))
        elif k == "black":
            f = L.render_black(kw["pid"], kw["dur"])
        elif k == "text":
            f = L.render_text(kw["pid"], kw["dur"], kw["lines"],
                              kw.get("fades", ("0.35", "0.35")), bg=kw.get("bg", "black"))
        files.append(f)
    return files

def render_audio2(out_wav, bursts):
    """Трек2 + шипение помех в моменты static -> wav 48k. Фейд на 213.5."""
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        return out_wav
    n = 1 + len(bursts)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", TRACK2]
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
              "afade=t=out:st=213.5:d=0.5[amix]")
    cmd += [";".join(parts), "-map", "[amix]", "-c:a", "pcm_s16le", "-ar", "48000", out_wav]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], file=sys.stderr)
        raise SystemExit("audio mix failed")
    return out_wav

def main():
    errs = check()
    if errs:
        print("ОШИБКИ ТАЙМЛАЙНА:")
        [print(" -", e) for e in errs]
        raise SystemExit(1)
    print(f"таймлайн v5-Б (CH 02, монтажный лист): {len(T)} кусков, {TOTAL}s — "
          f"проверен, все 25 S-кадров в деле"
          + (" (длительности предполагаются 10.0с)" if ASSUME else ""))
    if ASSUME:
        return
    files = render_all()
    print(f"отрендерено/найдено кусков: {len(files)}")
    lst = os.path.join(BUILD, "film_list_ch2.txt")
    with open(lst, "w") as fp:
        for f in files:
            fp.write(f"file '{f}'\n")
    cat = os.path.join(BUILD, "film_cat_ch2.mp4")
    if os.path.exists(cat):
        newest = max(os.path.getmtime(f) for f in files)
        if os.path.getmtime(cat) < newest - 2:
            os.remove(cat)
    if not (os.path.exists(cat) and os.path.getsize(cat) > 1000000):
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                            "-i", lst, "-c", "copy", cat], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1200:], file=sys.stderr); raise SystemExit("concat fail")
    aud = render_audio2(os.path.join(BUILD, "audio_final_ch2.wav"), BURSTS)
    out = os.path.join(BUILD, "ch2_film.mp4")
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
