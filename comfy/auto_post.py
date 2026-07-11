#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Контент-завод на ComfyUI → Telegram (автопилот).

Один прогон:
  1) берёт следующий текст (сценарий+caption) из ротации по дням;
  2) подставляет сценарий в ComfyUI-воркфлоу (talking-avatar) и запускает генерацию через API;
  3) ждёт готовности, забирает готовое видео;
  4) постит видео + caption в Telegram-канал.

Запускать по расписанию (cron) на машине, где крутится ComfyUI.
Пример cron (каждый день в 10:00):
  0 10 * * *  /usr/bin/python3 /path/to/auto_post.py >> /path/to/factory.log 2>&1

ComfyUI сам НЕ постит и НЕ расписывает — это делает этот скрипт. Никаких OAuth/коннекторов.
"""

import os
import io
import json
import time
import copy
import urllib.request
import urllib.parse

# ---------- НАСТРОЙКИ (можно через env) ----------
# Comfy Cloud: base = https://cloud.comfy.org, эндпоинты с префиксом /api, ключ в X-API-Key.
# Локальный ComfyUI: base = http://127.0.0.1:8188, префикс пустой, ключ не нужен.
COMFY_URL     = os.environ.get("COMFY_URL", "https://cloud.comfy.org")
COMFY_API_KEY = os.environ.get("COMFY_API_KEY", "")                    # ключ из cloud.comfy.org (тариф Standard+)
API_PREFIX    = os.environ.get("COMFY_API_PREFIX", "/api")             # "/api" для облака, "" для локального
WORKFLOW      = os.environ.get("COMFY_WORKFLOW", "workflow_api.json")  # экспорт воркфлоу «Export (API)»
BOT_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID       = os.environ.get("TELEGRAM_CHAT_ID", "-1004380165542")

# Узел и поле воркфлоу, куда подставлять текст реплики (сценарий).
# Найди в своём воркфлоу id ноды с текстом для TTS и имя её input (обычно "text").
SCRIPT_NODE_ID    = os.environ.get("COMFY_SCRIPT_NODE_ID", "")       # напр. "12"
SCRIPT_NODE_FIELD = os.environ.get("COMFY_SCRIPT_NODE_FIELD", "text")

# ---------- РОТАЦИЯ ТЕКСТОВ ----------
TEXTS = [
    {"script": "Красивые волосы — это не магия, а правильный уход и хороший мастер. Приходи в ara studio в Бресте.",
     "caption": "💇‍♀️ <b>Красивые волосы — это не магия</b>\n\nПравильный уход и руки мастера решают всё.\n\n📍 Брест · ara_studio · 📲 директ\n#ara_studio_brest #брест #парикмахербрест"},
    {"script": "Не жди особого случая, чтобы нравиться себе. Запишись и приходи.",
     "caption": "✨ <b>Повод — это ты</b>\n\nНе жди праздника, чтобы нравиться себе.\n\n📍 Брест · 📲 директ\n#ara_studio_brest #брест #стрижка"},
    {"script": "Хочешь укладку, которая держится весь день? Всё дело в уходе и технике мастера.",
     "caption": "💫 <b>Укладка, которая держится</b>\n\nСекрет не в лаке, а в уходе и технике.\n\n📍 Брест · 📲 директ\n#ara_studio_brest #брест #укладка"},
    {"script": "Правильная стрижка молодит лучше любого крема. Подберём форму под тебя.",
     "caption": "💇‍♀️ <b>Стрижка, которая молодит</b>\n\nФорма под черты лица — и ты свежее.\n\n📍 Брест · 📲 директ\n#ara_studio_brest #брест #стрижка"},
    {"script": "Боишься испортить волосы окрашиванием? С грамотным мастером цвет — это забота.",
     "caption": "🎨 <b>Цвет без вреда</b>\n\nОкрашивание у профи — про здоровье волос.\n\n📍 Брест · 📲 директ\n#ara_studio_brest #брест #окрашивание"},
]


def _headers(extra=None):
    h = {}
    if COMFY_API_KEY:
        h["X-API-Key"] = COMFY_API_KEY
    if extra:
        h.update(extra)
    return h


def _get(path, raw=False):
    req = urllib.request.Request(COMFY_URL + API_PREFIX + path, headers=_headers())
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    return data if raw else json.loads(data.decode("utf-8"))


def _post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(COMFY_URL + API_PREFIX + path, data=data,
                                 headers=_headers({"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def pick_text():
    idx = int(time.time() // 86400) % len(TEXTS)
    return TEXTS[idx]


def run_comfy(script_text):
    """Загружает воркфлоу (API-формат), подставляет текст, запускает, ждёт видео, возвращает bytes."""
    with open(WORKFLOW, "r", encoding="utf-8") as f:
        wf = json.load(f)

    if SCRIPT_NODE_ID and SCRIPT_NODE_ID in wf:
        wf[SCRIPT_NODE_ID]["inputs"][SCRIPT_NODE_FIELD] = script_text
    else:
        print("⚠️  SCRIPT_NODE_ID не задан/не найден — сценарий не подставлен. "
              "Укажи id ноды с текстом TTS в COMFY_SCRIPT_NODE_ID.")

    resp = _post("/prompt", {"prompt": wf})
    prompt_id = resp["prompt_id"]
    print("ComfyUI prompt_id:", prompt_id)

    # ждём завершения
    while True:
        time.sleep(5)
        hist = _get(f"/history/{prompt_id}")
        if prompt_id in hist:
            outputs = hist[prompt_id]["outputs"]
            for node_out in outputs.values():
                for key in ("gifs", "videos", "images"):
                    if key in node_out and node_out[key]:
                        v = node_out[key][0]
                        params = urllib.parse.urlencode({
                            "filename": v["filename"], "subfolder": v.get("subfolder", ""), "type": v.get("type", "output")
                        })
                        return _get("/view?" + params, raw=True)
            raise RuntimeError("Генерация завершилась, но видео в outputs не найдено — проверь ноду сохранения (SaveVideo/VHS).")


def post_telegram(video_bytes, caption):
    """Отправляет видео (bytes) в Telegram через multipart sendVideo."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    boundary = "----factoryboundary"
    parts = []

    def field(name, value):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))

    field("chat_id", CHAT_ID)
    field("caption", caption)
    field("parse_mode", "HTML")
    field("supports_streaming", "true")
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"reel.mp4\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n".encode("utf-8") + video_bytes + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        res = json.loads(r.read().decode("utf-8"))
    print("Telegram:", "✅ ok" if res.get("ok") else res)
    return res


def main():
    if not BOT_TOKEN:
        raise SystemExit("❌ Задай TELEGRAM_BOT_TOKEN")
    t = pick_text()
    print("Тема дня:", t["script"][:60], "...")
    video = run_comfy(t["script"])
    post_telegram(video, t["caption"])
    print("Готово.")


if __name__ == "__main__":
    main()
