#!/usr/bin/env python3
"""Мобильный фикс: перекодировка ch2/ch3 в H.264 High@4.0 + AAC 48 кГц.

Причина бага: ch2/ch3 закодированы с level 6.2 — мобильные декодеры
(iOS/Android аппаратный H.264) поддерживают максимум 5.2, поэтому
на телефонах 2-й и 3-й клипы не запускаются. ch1 (level 4.0) играет.

Схема (непрерывный звук, чанковая сборка с resume):
  1) аудио кодируется ЦЕЛИКОМ одним проходом (48 кГц) — без разрывов
  2) видео кодируется чанками по 900 кадров (30 с), каждый ~30-60 с
     кодирования; завершённые чанки пропускаются при повторном запуске
  3) чанки склеиваются -c copy, мукс с целым аудио, +faststart

Запуск: python3 tools/fix_mobile.py ch2|ch3
"""
import subprocess, sys, os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(BASE, ".build_film")
os.makedirs(BUILD, exist_ok=True)

FILES = {
    "ch2": ("video/ch2_night.mp4", "video/ch2_night.mobile.mp4", 214.0),
    "ch3": ("video/ch3_dawn.mp4", "video/ch3_dawn.mobile.mp4", 258.733),
}

V_ARGS = [
    "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
    "-preset", "medium", "-crf", "20",
    "-maxrate", "2.6M", "-bufsize", "5.2M",
    "-pix_fmt", "yuv420p", "-g", "60", "-keyint_min", "6",
    "-r", "30", "-fps_mode", "cfr",
]
A_ARGS = ["-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-ac", "2"]


def run(cmd, tag):
    print(f"[{tag}] {' '.join(cmd[:6])} ...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], file=sys.stderr)
        raise SystemExit(f"[{tag}] FAIL rc={r.returncode}")
    print(f"[{tag}] ok", flush=True)


def main(which):
    src, dst, dur = FILES[which]
    src_p, dst_p = os.path.join(BASE, src), os.path.join(BASE, dst)
    tag = which
    chunk_frames, chunk_sec = 900, 30.0
    total_frames = int(round(dur * 30))
    n_chunks = (total_frames + chunk_frames - 1) // chunk_frames
    print(f"[{tag}] {src}: {dur}s = {total_frames} кадров, {n_chunks} чанков", flush=True)

    # 1) целое аудио 48 кГц
    aud_p = os.path.join(BUILD, f"{which}_audio.m4a")
    if not os.path.exists(aud_p):
        run(["ffmpeg", "-y", "-i", src_p, "-vn"] + A_ARGS + [aud_p], f"{tag}/audio")

    # 2) видеок чанки (без звука), resume по факту файла
    done = []
    for i in range(n_chunks):
        start = i * chunk_sec
        frames = min(chunk_frames, total_frames - i * chunk_frames)
        if frames <= 0:
            break
        cp = os.path.join(BUILD, f"{which}_v{i:02d}.mp4")
        done.append(cp)
        if os.path.exists(cp) and os.path.getsize(cp) > 10000:
            print(f"[{tag}] chunk {i} уже есть, skip", flush=True)
            continue
        run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", src_p, "-an"]
            + V_ARGS + ["-frames:v", str(frames), cp], f"{tag}/v{i:02d}")

    # 3) concat видео
    lst = os.path.join(BUILD, f"{which}_list.txt")
    with open(lst, "w") as f:
        for p in done:
            f.write(f"file '{p}'\n")
    cat_p = os.path.join(BUILD, f"{which}_video_cat.mp4")
    if not os.path.exists(cat_p):
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat_p], f"{tag}/concat")

    # 4) мукс + faststart
    run(["ffmpeg", "-y", "-i", cat_p, "-i", aud_p,
         "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
         "-movflags", "+faststart", dst_p], f"{tag}/mux")

    # проверка
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=level,profile,pix_fmt,width,height",
         "-show_entries", "format=duration,size",
         "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate",
         "-of", "json", dst_p], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    print(json.dumps(info, indent=1, ensure_ascii=False))
    mb = float(info["format"]["size"]) / 1e6
    print(f"[{tag}] ГОТОВО: {dst} {mb:.1f} MB", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ch2")
