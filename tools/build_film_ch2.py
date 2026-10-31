#!/usr/bin/env python3
"""Сборка клипа CH 02 «Смени канал» · NIGHT (v5) — полностью из 16 AI-кадров N01-N16.

Ночная версия той же идеи: город и ночью бывает «серым» (приглушённый натрий,
пустые улицы) и «живым» (неон, дождь, отражения). Переключение канала —
та же вспышка помех на «СМЕНИ КАНАЛ».

Арка NIGHT:
  пролог (дождь начинается, город пуст) -> куплет (DIM-ночь) -> брейк-лужа
  -> СМЕНИ КАНАЛ -> неоновый канал (дроп 1) -> выдох -> живая ночная фактура
  (дроп 2: поезд/танцпол/рынок/переулок) -> пожарная лестница наверх ->
  крыша и горизонт (финал) -> тишина -> последний проход + тизер CH 03 (Q14:
  золотой рассвет из ch1 — каналы пересекаются) -> титр.

Таймлайн по анализу Трек2.mp3 (214.03с):
  0-16 интро | 16-38 куплет | 38-46 брейк | 46-74 ДРОП 1 | 74-82 брейк |
  82-142 ДРОП 2 | 142-156 переход | 156-184 ФИНАЛ | 184-198 брейк+тишина |
  198-214 последний проход | 214-217.3 титр.

Запуск: python3 tools/build_film_ch2.py [--check-only]
"""
import os, sys, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_lib as L

BUILD = L.BUILD
TOTAL = 217.300
TRACK2 = "/home/z/my-project/upload/Трек2.mp3"
S = L.SLOW2

# ---- ночные грейды ----
# «Серый» ночной канал: почти монохром, холодный синий отлив, виньетка, зерно.
# Хрома гасится в конце цепочки (после зерна) — по завету v4.
DIM = ("eq=saturation=0.20:contrast=1.04:brightness=-0.04,"
       "vignette=0.48,noise=alls=6:allf=t,"
       "eq=saturation=0.16,colorbalance=bs=0.05:bm=0.03")
# «Живой» ночной канал: неон вперёд, глубокие тени, тёплые верха/холодные середины.
NEON = ("eq=saturation=1.32:contrast=1.16:gamma=0.97:brightness=-0.02,"
        "colorbalance=rs=0.02:bs=-0.03:rm=0.05:bm=-0.05:rh=0.06:bh=-0.04,"
        "unsharp=5:5:0.6,noise=alls=4:allf=t")

G, C = DIM, NEON
Q = L.GEN                       # Q("N01") -> aivideo/film_ch2/N01.mp4
GEN = lambda n: os.path.join(L.BASE, "aivideo", "film_ch2", f"{n}.mp4")
CH1 = lambda n: os.path.join(L.BASE, "aivideo", "film", f"{n}.mp4")  # кадры ch1 (мост-тизер)

# фактические длительности N-кадров (ffprobe, для проверок)
QDUR = {}
for _name in ["N01","N02","N03","N04","N05","N06","N07","N08","N09","N10",
              "N11","N12","N13","N14","N15","N16"]:
    _p = GEN(_name)
    if not os.path.exists(_p):
        raise SystemExit(f"нет {_p} — v5 собирается только из 16/16")
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

# ================= ПРОЛОГ: ночь опускается (0-16) =================
seg(0.00, 0.40, "black", "v5blk1", dur=0.40)
src(0.40, 8.80, "v5p01", "N01", 0.00, 4.20, G, slow=True)           # аэро: дождь начинается
src(8.80, 16.00, "v5p02", "N02", 0.00, 3.60, G, slow=True)          # одинокая походка мимо витрин

# ================= КУПЛЕТ 1: приглушённая ночь (16-38) =================
src(16.00, 21.00, "v5p03", "N03", 0.00, 2.50, G, slow=True)         # портрет, неон скользит по лицу
src(21.00, 27.00, "v5p04", "N02", 3.60, 6.60, G, slow=True)         # походка продолжается
src(27.00, 33.00, "v5p05", "N04", 0.00, 3.00, G, slow=True)         # лужа: город в отражении
src(33.00, 38.00, "v5p06", "N01", 4.20, 6.70, G, slow=True)         # аэро: город мерцает вдалеке

# ================= БРЕЙК 1: зеркало + переключение (38-46) =================
src(38.00, 44.20, "v5p07", "N04", 3.00, 6.10, "", slow=True)        # капля ломает отражение (цвет без грейда)
seg(44.20, 44.60, "static", "v5st1", dur=0.40, band_y=0.35)
seg(44.60, 44.80, "text", "v5tf1", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])
seg(44.80, 46.00, "black", "v5blk2", dur=1.20)                      # тишина перед дропом

# ================= ДРОП 1: неоновый канал (46-74) =================
src(46.00, 52.00, "v5p08", "N05", 0.00, 3.00, C, slow=True)         # мокрая улица, проход сквозь неон
typ(52.00, 54.00, "v5t1", "N05", 3.00, 5.00, "ВЗГЛЯНИ ИНАЧЕ")
src(54.00, 60.00, "v5p09", "N06", 0.00, 3.00, C, slow=True)         # перекрёсток: красный -> зелёный
typ(60.00, 62.00, "v5t2", "N06", 3.00, 5.00, "МИР НЕ ИЗМЕНИЛСЯ")
src(62.00, 68.00, "v5p10", "N07", 0.00, 3.00, C, slow=True)         # ночной рынок, огонь вока
typ(68.00, 70.00, "v5t3", "N07", 3.00, 5.00, "ТЫ СМОТРИШЬ ИНАЧЕ")
src(70.00, 74.00, "v5p11", "N14", 0.00, 2.00, C, slow=True)         # забегаловка 24ч, пар от кофе

# ================= БРЕЙК 2: выдох (74-82) =================
src(74.00, 79.60, "v5p12", "N08", 0.00, 2.80, G, slow=True)         # переулок, кот, вывеска барахлит
seg(79.60, 80.00, "static", "v5st2", dur=0.40, band_y=0.62)
seg(80.00, 80.20, "text", "v5tf2", dur=0.20, fades=("0", "0"),
    lines=[("С М Е Н И   К А Н А Л", 132, "(h-th)/2", "white")])
seg(80.20, 82.00, "black", "v5blk3", dur=1.80)

# ================= ДРОП 2: живая ночная фактура (82-142) =================
src(82.00, 88.00, "v5p13", "N09", 0.00, 3.00, C, slow=True)         # поезд, полосы света
src(88.00, 94.00, "v5p14", "N10", 0.00, 3.00, C, slow=True)         # танцпол, строб
src(94.00, 100.00, "v5p15", "N08", 2.80, 5.80, C, slow=True)        # неон заливает стену граффити
typ(100.00, 102.00, "v5t4", "N07", 5.00, 7.00, "НЕ ЖДИ ЗНАКА СВЫШЕ")
src(102.00, 108.00, "v5p16", "N07", 3.00, 6.00, C, slow=True)       # рынок: тепло и пар
src(108.00, 114.00, "v5p17", "N05", 3.00, 6.00, C, slow=True)       # неоновая улица дальше
typ(114.00, 116.00, "v5t5", "N06", 5.00, 7.00, "ИНОГДА ДОСТАТОЧНО")
src(116.00, 122.00, "v5p18", "N06", 3.00, 6.00, C, slow=True)       # машины сквозь лужи
src(122.00, 128.00, "v5p19", "N14", 2.00, 5.00, C, slow=True)       # diner: свет на тротуар
src(128.00, 134.00, "v5p20", "N10", 3.00, 6.00, C, slow=True)       # танцпол: пик
typ(134.00, 136.00, "v5t6", "N05", 6.00, 8.00, "СДЕЛАТЬ ШАГ ПОБЛИЖЕ")
src(136.00, 142.00, "v5p21", "N09", 3.00, 6.00, C, slow=True)       # поезд уносится вдаль

# ================= ПЕРЕХОД: наверх (142-156) =================
src(142.00, 150.00, "v5p22", "N11", 0.00, 4.00, C, slow=True,
    extra="fade=t=in:st=0:d=0.7,fade=t=out:st=7.3:d=0.7")           # пожарная лестница
src(150.00, 155.60, "v5p23", "N11", 4.00, 6.80, C, slow=True,
    extra="fade=t=in:st=0:d=0.7,fade=t=out:st=4.9:d=0.7")           # выход на крышу
seg(155.60, 156.00, "static", "v5st3", dur=0.40, band_y=0.80)

# ================= ФИНАЛ: крыша и горизонт (156-184) =================
src(156.00, 164.00, "v5p24", "N12", 0.00, 4.00, C, slow=True)       # капюшон снят, город дышит
typ(164.00, 166.00, "v5t7", "N12", 4.00, 6.00, "ПУСТЬ МЕНЯЕТСЯ ЗВУК")
src(166.00, 172.00, "v5p25", "N13", 0.00, 3.00, C, slow=True)       # звёзды гаснут
typ(172.00, 174.00, "v5t8", "N13", 3.00, 5.00, "ИНОГДА НОВЫЙ ВЗГЛЯД —")
src(174.00, 180.00, "v5p26", "N15", 0.00, 3.00, C, slow=True)       # мост: световые следы
typ(180.00, 182.00, "v5t9", "N16", 0.00, 2.00, "ЭТО ВЫХОД ИЗ КРУГА")
src(182.00, 184.00, "v5p27", "N15", 3.00, 4.00, C, slow=True)       # машина уезжает в неон

# ================= БРЕЙК 3 + ТИШИНА (184-198) =================
src(184.00, 192.00, "v5p28", "N13", 5.00, 9.00, C, slow=True,
    extra="fade=t=in:st=0:d=0.9,fade=t=out:st=6.3:d=0.9")           # небо на грани
src(192.00, 196.00, "v5p29", "N12", 6.00, 8.00, C, slow=True,
    extra="fade=t=out:st=3.3:d=0.7")                                # крыша гаснет
seg(196.00, 198.00, "black", "v5blk4", dur=2.00)                    # тишина (провал на 196с)

# ================= ПОСЛЕДНИЙ ПРОХОД (198-214) =================
seg(198.00, 198.40, "static", "v5st4", dur=0.40, band_y=0.20)
src(198.40, 204.00, "v5p30", "N16", 0.00, 2.80, C, slow=True)       # шаг к свету
src(204.00, 210.00, "v5p31", "N16", 5.60, 8.60, C, slow=True)       # камера поднимается
src(210.00, 214.00, "v5p32", "Q14", 7.00, 9.00, C, slow=True,
    osd="CH 03")                                                    # тизер: золотой рассвет ch1

# ================= ТИТР =================
seg(214.00, 217.30, "text", "v5titl", dur=3.30, fades=("0.40", "0.40"),
    lines=[("С М Е Н И   К А Н А Л", 108, "(h-th)/2-90", "white"),
           ("N I G H T   ·   ГРЯЗНЫЙ ГЕНА  ·  DIRTYGEN", 30, "(h-th)/2+120", "0xC8C8C8")])

BURSTS = [(44.2, 0.30), (79.6, 0.30), (155.6, 0.34), (198.0, 0.30)]

# путь источника: N-кадры из film_ch2, мост Q14 — из film (ch1)
def qpath(q):
    return CH1(q) if q.startswith("Q") else GEN(q)

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
            f = L.render_text(kw["pid"], kw["dur"], kw["lines"], kw.get("fades", ("0.35", "0.35")))
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
    print(f"таймлайн v5 (CH 02 NIGHT): {len(T)} кусков, {TOTAL}s — проверен, все 16 N-кадров в деле")
    if "--check-only" in sys.argv:
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
