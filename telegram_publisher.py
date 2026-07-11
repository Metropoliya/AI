#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Контент-завод → Telegram.

Берёт пакет постов (видео/фото + текст) и публикует их в Telegram-канал
через Bot API. Ссылки на видео Telegram скачивает сам, поэтому достаточно
передать URL (например, CDN-ссылку из Higgsfield) — файл качать не нужно.

Использование:
    # 1) задать секреты (создать бота у @BotFather, добавить его в канал админом)
    export TELEGRAM_BOT_TOKEN="1234567890:AA..."
    export TELEGRAM_CHAT_ID="@my_channel"        # или числовой -1001234567890

    # 2) опубликовать пакет
    python telegram_publisher.py posts.json

    # опции:
    #   --delay 5        пауза (сек) между постами, чтобы не ловить лимиты
    #   --dry-run        показать, что было бы отправлено, без запросов

Формат posts.json — список постов:
    [
      {"type": "video", "url": "https://.../reel.mp4", "caption": "Текст поста..."},
      {"type": "photo", "url": "https://.../pic.png",  "caption": "..."},
      {"type": "text",  "caption": "Просто текстовый пост"}
    ]
caption необязателен; для type=text отправляется только текст.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse

API = "https://api.telegram.org"

# Лимиты Telegram: подпись к медиа — 1024 символа, обычное сообщение — 4096.
CAPTION_LIMIT = 1024
TEXT_LIMIT = 4096


def _call(token: str, method: str, params: dict) -> dict:
    """Один вызов Bot API (multipart не нужен — шлём URL строкой)."""
    url = f"{API}/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_video(token, chat_id, video_url, caption="", parse_mode="HTML"):
    return _call(token, "sendVideo", {
        "chat_id": chat_id,
        "video": video_url,
        "caption": caption[:CAPTION_LIMIT],
        "parse_mode": parse_mode,
        "supports_streaming": "true",
    })


def send_photo(token, chat_id, photo_url, caption="", parse_mode="HTML"):
    return _call(token, "sendPhoto", {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption[:CAPTION_LIMIT],
        "parse_mode": parse_mode,
    })


def send_text(token, chat_id, text, parse_mode="HTML"):
    return _call(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text[:TEXT_LIMIT],
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    })


def publish_one(token, chat_id, post, dry_run=False):
    ptype = post.get("type", "text")
    caption = post.get("caption", "")
    url = post.get("url", "")

    if dry_run:
        print(f"  [dry-run] {ptype} url={url[:60]} caption={caption[:50]!r}")
        return {"ok": True, "dry_run": True}

    if ptype == "video":
        return send_video(token, chat_id, url, caption)
    if ptype == "photo":
        return send_photo(token, chat_id, url, caption)
    if ptype == "text":
        return send_text(token, chat_id, caption)
    raise ValueError(f"Неизвестный тип поста: {ptype!r}")


def publish_batch(posts, token=None, chat_id=None, delay=3.0, dry_run=False):
    """Публикует список постов по очереди. Возвращает список результатов."""
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit(
            "❌ Не заданы TELEGRAM_BOT_TOKEN и/или TELEGRAM_CHAT_ID "
            "(env-переменные или аргументы функции)."
        )

    results = []
    total = len(posts)
    for i, post in enumerate(posts, 1):
        print(f"→ [{i}/{total}] публикую пост ({post.get('type', 'text')})...")
        try:
            res = publish_one(token, chat_id, post, dry_run=dry_run)
            ok = res.get("ok")
            print(f"   {'✅ ок' if ok else '⚠️ ' + str(res)}")
            results.append(res)
        except Exception as e:  # noqa: BLE001 — хотим продолжить пакет при ошибке одного поста
            print(f"   ❌ ошибка: {e}")
            results.append({"ok": False, "error": str(e)})
        if i < total and not dry_run:
            time.sleep(delay)

    ok_count = sum(1 for r in results if r.get("ok"))
    print(f"\nГотово: {ok_count}/{total} постов опубликовано.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Публикация пакета постов в Telegram.")
    parser.add_argument("posts", help="Путь к JSON-файлу со списком постов (например posts.json)")
    parser.add_argument("--delay", type=float, default=3.0, help="Пауза между постами, сек (по умолчанию 3)")
    parser.add_argument("--dry-run", action="store_true", help="Не отправлять, только показать план")
    args = parser.parse_args()

    with open(args.posts, "r", encoding="utf-8") as f:
        posts = json.load(f)

    publish_batch(posts, delay=args.delay, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
