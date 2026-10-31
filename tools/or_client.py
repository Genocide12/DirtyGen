#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OR-клиент DirtyGen — бесплатные модели OpenRouter для задач пайплайна CH 02.

Что даёт (ключ рабочий, протестировано 2026-11-01):
  status                     — остаток дневного лимита бесплатных запросов
  chat "промпт"             — текстовый вызов (авто-выбор мощной бесплатной модели)
  vision <img> "промпт"     — VLM-проверка кадра клипа (nemotron-3.5-super-vl:free)

Ключ читается из /home/z/my-project/.secrets/openrouter.key — файл ВНЕ git-репозитория
(добавлен в .gitignore), в коммит попасть не может.

Результаты тестов 2026-11-01 (лимит 50 запросов/день):
  chat   nvidia/nemotron-3-ultra-550b-a55b:free — ✅ 10.4с, валидный JSON сегментации
         сцены, HERO-дескрипторы в каждом промпте, $0
  vision nvidia/nemotron-3.5-super-vl:free      — ✅ детальный QC-разбор кадра,
         находит AI-артефакты, оценка N/10
  music  google/lyria-3-pro-preview и lyria-3-clip-preview — ❌ 403 ГЕО-БЛОК
         («not available in your region») из этой песочницы. Не тратить запросы.

Важно: бесплатных ВИДЕО-моделей на OpenRouter нет (0 из 452). Видео-сегменты клипа
генерирует внутренний API (enrich_v5.sh); OR-модели — «мозг» пайплайна: сегментация
сцен, промпты, контроль кадров (tools/qc_shot_or.py).
"""
import base64
import json
import sys
import time
import urllib.request
import urllib.error

KEY_PATH = "/home/z/my-project/.secrets/openrouter.key"
BASE = "https://openrouter.ai/api/v1"

# Приоритет мощных бесплатных текстовых моделей (фолбэк сверху вниз)
FREE_CHAT_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # 550B MoE, ctx 1M — мощнейшая бесплатная
    "nvidia/nemotron-3.5-lightning:free",      # быстрая, ctx 1M
    "thinkingmachines/inkling:free",           # ctx 1M
    "google/gemma-4-31b-it:free",
    "openrouter/free",                         # авто-роутер бесплатных
]
FREE_VISION_MODEL = "nvidia/nemotron-3.5-super-vl:free"   # вход: text+image
FREE_MUSIC_MODEL = "google/lyria-3-pro-preview"           # выход: audio, бесплатно (превью)


class ORKeyError(RuntimeError):
    """Ключ отсутствует/истёк — нужен новый от пользователя."""


def _key():
    try:
        k = open(KEY_PATH).read().strip()
    except FileNotFoundError:
        raise ORKeyError("нет %s (ключ потерян при откате диска или ещё не создан)" % KEY_PATH)
    if not k:
        raise ORKeyError("файл ключа пуст")
    return k


def _req(path, payload=None, timeout=240):
    key = _key()
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code == 401:
            raise ORKeyError("OpenRouter отклонил ключ (401): " + body[:200])
        raise RuntimeError("OpenRouter HTTP %d: %s" % (e.code, body[:300]))


def key_status():
    """Остаток дневного лимита бесплатных запросов и баланс."""
    info = _req("/key").get("data", {})
    fd = info.get("free_model_daily_requests") or {}
    return {
        "label": info.get("label"),
        "usage": info.get("usage"),
        "limit": info.get("limit"),
        "limit_remaining": info.get("limit_remaining"),
        "is_free_tier": info.get("is_free_tier"),
        "free_daily_used": fd.get("used"),
        "free_daily_limit": fd.get("limit"),
        "free_daily_remaining": fd.get("remaining"),
    }


def chat(prompt, system=None, model=None, max_tokens=2000):
    """Текстовый вызов с авто-фолбэком по списку мощных бесплатных моделей."""
    models = [model] if model else list(FREE_CHAT_MODELS)
    last = None
    for m in models:
        msgs = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}]
        try:
            resp = _req("/chat/completions",
                        {"model": m, "messages": msgs, "max_tokens": max_tokens})
            msg = resp["choices"][0]["message"]
            return {"model": resp.get("model", m), "content": msg.get("content") or "",
                    "usage": resp.get("usage", {})}
        except ORKeyError:
            raise
        except Exception as e:  # 429/5xx/иное — пробуем следующую модель
            last = "%s: %s" % (m, str(e)[:160])
            time.sleep(2)
    raise RuntimeError("все бесплатные модели недоступны: " + str(last))


def vision(image_path, prompt, model=FREE_VISION_MODEL, max_tokens=1000):
    """VLM-анализ кадра (jpg/png): контроль качества кадров клипа."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = "png" if image_path.lower().endswith(".png") else "jpeg"
    resp = _req("/chat/completions", {
        "model": model, "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/%s;base64,%s" % (ext, b64)}},
        ]}],
    })
    return {"model": resp.get("model", model),
            "content": resp["choices"][0]["message"].get("content") or "",
            "usage": resp.get("usage", {})}


def music(prompt, out_path="/tmp/or_music.wav", max_tokens=4000):
    """ЭКСПЕРИМЕНТ: бесплатная музыка (google/lyria-3-pro-preview).
    Формат аудио-ответа может отличаться — при неожиданной форме сохраняет сырой JSON."""
    resp = _req("/chat/completions", {
        "model": FREE_MUSIC_MODEL, "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]})
    msg = resp["choices"][0]["message"]
    audio = msg.get("audio") or {}
    data = audio.get("data") or audio.get("b64_json")
    if data:
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(data))
        return {"saved": out_path, "format": audio.get("format"), "model": FREE_MUSIC_MODEL}
    debug = out_path + ".debug.json"
    with open(debug, "w") as f:
        json.dump(resp, f, ensure_ascii=False, indent=1)
    return {"saved": None, "debug_json": debug,
            "text": (msg.get("content") or "")[:400], "model": FREE_MUSIC_MODEL}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    try:
        if cmd == "status":
            print(json.dumps(key_status(), ensure_ascii=False, indent=2))
        elif cmd == "chat":
            r = chat(" ".join(sys.argv[2:]))
            print("model:", r["model"])
            print(r["content"])
        elif cmd == "vision":
            r = vision(sys.argv[2], " ".join(sys.argv[3:]))
            print("model:", r["model"])
            print(r["content"])
        elif cmd == "music":
            print(json.dumps(music(" ".join(sys.argv[2:])), ensure_ascii=False, indent=2))
        else:
            print(__doc__)
    except ORKeyError as e:
        print("ORKeyError:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
