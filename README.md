# AI Project

Инструменты для контент-завода и аудиокниг.

## 🏭 Контент-завод → Telegram

Генерируем контент (видео-рилсы с AI-аватаром + тексты постов) и публикуем пачкой в Telegram-канал.

### Файлы
- **`content_factory.ipynb`** — Colab-ноутбук: вставляешь токен/канал и пакет постов → публикует в Telegram. Рекомендуемый способ (Telegram доступен из Colab).
- **`telegram_publisher.py`** — тот же публикатор как CLI-скрипт (для локального запуска / автоматизации).
- **`posts.json`** — пример пакета постов.

### Быстрый старт (Colab)
1. Создай бота у [@BotFather](https://t.me/BotFather): `/newbot` → скопируй токен.
2. Добавь бота **администратором** в свой канал (право «Публикация сообщений»).
3. Открой `content_factory.ipynb` в Colab, впиши `BOT_TOKEN` и `CHAT_ID` (`@канал` или `-100...`), вставь свои посты и запусти ячейки сверху вниз.

### Быстрый старт (CLI)
```bash
export TELEGRAM_BOT_TOKEN="1234567890:AA..."
export TELEGRAM_CHAT_ID="@my_channel"
python telegram_publisher.py posts.json --delay 5
```
`--dry-run` — показать план без отправки.

### Формат поста
```json
{"type": "video", "url": "https://.../reel.mp4", "caption": "Текст поста с #хэштегами"}
```
`type`: `video` | `photo` | `text`. Для медиа Telegram скачивает файл по `url` сам.

> ⚠️ Токен бота — секрет. Не коммить его в репозиторий: держи в форме Colab или в переменной окружения.

## 🎧 Аудиокниги
- `fb2.ipynb` — fb2 → озвучка (edge-tts).
- `Voice Book v 3.ipynb` — pdf → озвучка.
- `Voice Video.ipynb` — видео с озвучкой.
