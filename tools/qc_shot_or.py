#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VLM-контроль качества AI-сегментов клипа CH 02 через OpenRouter (бесплатно).

Извлекает средний кадр из каждого S*.mp4 (ffmpeg), отправляет в
nvidia/nemotron-3.5-super-vl:free, получает вердикт «живое видео / AI-артефакт»
и оценку N/10. Бюджет: 1 запрос на сегмент из 50/день (25 сегментов = половина лимита).

Usage:
  python3 tools/qc_shot_or.py                  # все aivideo/film_ch2/S*.mp4
  python3 tools/qc_shot_or.py S01 S05 S12      # конкретные сегменты
  python3 tools/qc_shot_or.py --min 7          # порог оценки (default 6)

Выход: таблица «сегмент | оценка | вердикт», список провалившихся для перегенерации.
"""
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import or_client  # noqa: E402

SEG_DIR = "aivideo/film_ch2"
QC_PROMPT = (
    "Ты — контролёр качества AI-видео для музыкального клипа DIRTYGEN "
    "(тёмный электронный поп, ТВ-нуар, ночной город, неон, герой — мужчина 33 лет "
    "в чёрном пальто поверх тёмного худи). Это средний кадр 10-секундного сегмента. "
    "Опиши кратко (1-2 предложения), затем отдельной строкой вердикт по форме: "
    "VERDICT: OK — если это живое кинематографичное изображение без сильных "
    "артефактов, или VERDICT: BAD — если кадр расплывшийся/деградировавший/"
    "перегруженный мульти-экшеном. Ещё одной строкой: SCORE: N/10."
)


def mid_frame(video, out_jpg):
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video]).strip())
    t = max(0.1, dur / 2)
    subprocess.check_call(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", video,
         "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", out_jpg])
    return out_jpg


def parse_verdict(text):
    score = None
    m = re.search(r"SCORE:\s*(\d+)\s*/\s*10", text)
    if m:
        score = int(m.group(1))
    ok = None
    v = re.search(r"VERDICT:\s*(OK|BAD)", text)
    if v:
        ok = v.group(1) == "OK"
    if score is not None and ok is None:  # фолбэк: оценка >= порога = OK
        ok = True
    return ok, score


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mn = 6
    if "--min" in sys.argv:
        mn = int(sys.argv[sys.argv.index("--min") + 1])
    if args:
        vids = ["%s/%s.mp4" % (SEG_DIR, a) for a in args]
    else:
        vids = sorted(glob.glob("%s/S*.mp4" % SEG_DIR))
    if not vids:
        print("нет сегментов в %s (генерация ещё не дошла) — QC нечего проверять" % SEG_DIR)
        return
    print("QC %d сегментов через OpenRouter (лимит 50/день)..." % len(vids))
    bad = []
    for v in vids:
        name = os.path.basename(v)
        try:
            jpg = "/tmp/qc_" + name.replace(".mp4", ".jpg")
            mid_frame(v, jpg)
            r = or_client.vision(jpg, QC_PROMPT)
            ok, score = parse_verdict(r["content"])
            status = "OK " if (ok and (score or 0) >= mn) else "BAD"
            if status == "BAD":
                bad.append(name)
            print("%-9s %s %s/10 | %s" % (
                name, status, score if score is not None else "?",
                r["content"].replace("\n", " ")[:110]))
        except Exception as e:
            print("%-9s ERR %s" % (name, str(e)[:120]))
            bad.append(name)
    print("\nИтог: %d/%d OK (порог %d/10)" % (len(vids) - len(bad), len(vids), mn))
    if bad:
        print("На перегенерацию:", " ".join(b.replace(".mp4", "") for b in bad))


if __name__ == "__main__":
    main()
