#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OR-клиент DirtyGen (мульти-провайдер) — бесплатные модели для задач пайплайна CH 02.

Провайдеры (протестированы 2026-11-01):
  openrouter  — nemotron-3-ultra-550b (мощнейшая, 1M ctx), nemotron-3.5-super-vl (VLM-зрение);
                лимит 50 запросов/день, ключ 2 юзера рабочий
  orcarouter  — deepseek-v4.1-flash-free (JSON OK 11.2с), tencent-hy3-free (JSON OK 12.8с),
                glm-5.3-flash-free (JSON OK 21.1с при max_tokens>=3000), deepseek-v4-flash-free;
                Hacker-план бесплатный, рейт-лимит неизвестен (щедрее OpenRouter)

Команды:
  status                     — остатки лимитов по провайдерам
  chat "промпт"             — текстовый вызов (фолбэк: openrouter → orcarouter)
  vision <img> "промпт"     — VLM-проверка кадра (только openrouter super-vl:free)

Ключи: /home/z/my-project/.secrets/{openrouter,orca}.key — ВНЕ git (.gitignore).
При откате диска файлы пропадают → попросить у юзера заново.

Мёртвые ветки (не тратить время):
  teamorouter  — «free»-модели требуют пополненный кошелёк (400 insufficient_balance)
  tokenharbor  — 403 гео-блок региона песочницы
  openrouter music (Lyria) — 403 гео-блок
  БЕСПЛАТНОЙ ВИДЕО-генерации нигде нет: OpenRouter 0/452, OrcaRouter minimax-h3
  платно ($0.08-0.13/с, /v1/videos), видео-сегменты клипа — внутренний API (enrich_v5.sh).
"""
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

SECRETS = "/home/z/my-project/.secrets"

PROVIDERS = [
    {
        "name": "openrouter",
        "base": "https://openrouter.ai/api/v1",
        "key_file": SECRETS + "/openrouter.key",
        "chat_models": [
            "nvidia/nemotron-3-ultra-550b-a55b:free",   # 550B MoE, ctx 1M — топ
            "nvidia/nemotron-3.5-lightning:free",
            "openrouter/free",
        ],
        "vision_model": "nvidia/nemotron-3.5-super-vl:free",
    },
    {
        "name": "orcarouter",
        "base": "https://api.orcarouter.ai/v1",
        "key_file": SECRETS + "/orca.key",
        "chat_models": [
            "deepseek/deepseek-v4.1-flash-free",        # JSON OK за 11.2с
            "tencent/hy3-free",                          # JSON OK за 12.8с
            "z-ai/glm-5.3-flash-free",                  # брать max_tokens>=3000
        ],
        "vision_model": None,
    },
]


class ORKeyError(RuntimeError):
    """Все ключи отсутствуют/истёкли — нужен новый от пользователя."""


def _read_key(p):
    try:
        k = open(p).read().strip()
        return k or None
    except FileNotFoundError:
        return None


def _req(base, key, path, payload=None, timeout=240, method=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        base + path, data=data, method=method,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code == 401:
            raise ORKeyError("%s: ключ отвергнут (401): %s" % (base, body[:150]))
        raise RuntimeError("%s HTTP %d: %s" % (base, e.code, body[:300]))


def status():
    out = {}
    for p in PROVIDERS:
        key = _read_key(p["key_file"])
        if not key:
            out[p["name"]] = {"key": "нет файла ключа"}
            continue
        try:
            info = _req(p["base"], key, "/key").get("data", {}) if p["name"] == "openrouter" else {}
            if not info:
                # orcarouter: /key может не быть — лёгкая проверка /models
                _req(p["base"], key, "/models")
                info = {"note": "ключ работает (models ок)"}
            out[p["name"]] = {"key": "ok"}
            if p["name"] == "openrouter":
                fd = info.get("free_model_daily_requests") or {}
                out[p["name"]] = {
                    "key": "ok",
                    "free_daily_used": fd.get("used"),
                    "free_daily_limit": fd.get("limit"),
                    "free_daily_remaining": fd.get("remaining"),
                }
        except Exception as e:
            out[p["name"]] = {"key": "FAIL: " + str(e)[:120]}
    return out


def chat(prompt, system=None, model=None, max_tokens=3000):
    """Текстовый вызов: фолбэк по провайдерам → моделям. model='пров/модель' пинует модель."""
    pinned = None
    if model:
        for p in PROVIDERS:
            if model.startswith(p["name"] + "/"):
                pinned = (p["name"], model[len(p["name"]) + 1:])
                break
    errors = []
    for p in PROVIDERS:
        key = _read_key(p["key_file"])
        if not key:
            errors.append("%s: нет ключа" % p["name"])
            continue
        models = [pinned[1]] if (pinned and pinned[0] == p["name"]) else (
            [] if pinned else p["chat_models"])
        for m in models:
            msgs = ([{"role": "system", "content": system}] if system else []) + [
                {"role": "user", "content": prompt}]
            try:
                resp = _req(p["base"], key, "/chat/completions",
                            {"model": m, "messages": msgs, "max_tokens": max_tokens})
                msg = resp["choices"][0]["message"]
                return {"provider": p["name"], "model": resp.get("model", m),
                        "content": msg.get("content") or "", "usage": resp.get("usage", {})}
            except ORKeyError:
                errors.append("%s/%s: KEY" % (p["name"], m))
                break  # ключ мёртв — следующая модель этого провайдера тоже упадёт
            except Exception as e:
                errors.append("%s/%s: %s" % (p["name"], m, str(e)[:120]))
                time.sleep(2)
    raise RuntimeError("все провайдеры недоступны: " + "; ".join(errors[-4:]))


def vision(image_path, prompt, max_tokens=1200):
    """VLM-анализ кадра — только openrouter/nemotron-3.5-super-vl:free."""
    p = PROVIDERS[0]
    key = _read_key(p["key_file"])
    if not key:
        raise ORKeyError("нет ключа openrouter (нужен для vision)")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = "png" if image_path.lower().endswith(".png") else "jpeg"
    resp = _req(p["base"], key, "/chat/completions", {
        "model": p["vision_model"], "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/%s;base64,%s" % (ext, b64)}},
        ]}],
    })
    return {"provider": p["name"], "model": p["vision_model"],
            "content": resp["choices"][0]["message"].get("content") or "",
            "usage": resp.get("usage", {})}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    try:
        if cmd == "status":
            print(json.dumps(status(), ensure_ascii=False, indent=2))
        elif cmd == "chat":
            r = chat(" ".join(sys.argv[2:]))
            print("[%s] %s" % (r["provider"], r["model"]))
            print(r["content"])
        elif cmd == "vision":
            r = vision(sys.argv[2], " ".join(sys.argv[3:]))
            print("[%s] %s" % (r["provider"], r["model"]))
            print(r["content"])
        else:
            print(__doc__)
    except ORKeyError as e:
        print("ORKeyError:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
