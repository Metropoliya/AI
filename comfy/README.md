# 🏭 Контент-завод на Comfy Cloud → Telegram

Автопилот без своего железа: генерация рилса в **Comfy Cloud** (по API) + автопостинг в Telegram по расписанию.

```
[cron на любой машине/сервере]
  → auto_post.py
      → Comfy Cloud API  (сгенерить talking-avatar рилс)
      → Telegram Bot API (опубликовать видео + caption)
```
Никаких OAuth-коннекторов и мигающих сервисов — только API-ключи в env.

## Файлы
- **`auto_post.py`** — «мозг»: берёт текст дня → запускает воркфлоу в Comfy Cloud → забирает видео → постит в Telegram.

## Что нужно один раз
1. **Comfy Cloud** — тариф **Standard/Creator/Pro** (на Free API нет). Получи **API-ключ** в `cloud.comfy.org` → заголовок `X-API-Key`.
2. **Воркфлоу talking-avatar** в Comfy Cloud, который делает: фото аватара + текст → озвучка (TTS, желательно клон голоса) → lip-sync → видео 9:16. Собери/импортируй его в Comfy Cloud и нажми **Export → API** (получишь `workflow_api.json`).
3. **Telegram-бот** (токен `@BotFather`) + бот админом в канале.

## Запуск
```bash
export COMFY_API_KEY="твой_ключ"
export COMFY_WORKFLOW="/path/workflow_api.json"
export COMFY_SCRIPT_NODE_ID="12"          # id ноды с текстом TTS в твоём воркфлоу
export TELEGRAM_BOT_TOKEN="8947641675:AA..."
export TELEGRAM_CHAT_ID="-1004380165542"
python3 auto_post.py
```
Расписание (cron, ежедневно 10:00):
```
0 10 * * *  /usr/bin/python3 /path/auto_post.py >> /path/factory.log 2>&1
```
Тексты (сценарий+caption) — внутри `auto_post.py`, ротация по дням. Дописывай/меняй прямо там.

## ⚠️ Открытый вопрос (проверить до сборки)
Главное, что нужно подтвердить: **поддерживает ли Comfy Cloud кастомные ноды** для talking-avatar —
- image→video (Wan / аналог),
- TTS с **клоном твоего голоса** (XTTS / F5-TTS / подобное),
- **lip-sync** (LatentSync / Sonic / Wav2Lip).

Если Comfy Cloud даёт ставить нужные custom nodes и модели — пайплайн собирается целиком, и завод крутится сам. Если какие-то ноды недоступны в облаке — часть шагов (напр. клон голоса) заменим на внешний API (напр. отдельный TTS) внутри `auto_post.py`.

**План действий:**
1. Заводишь Comfy Cloud (Standard+) и API-ключ.
2. Проверяем, какие ноды/модели доступны → собираем воркфлоу talking-avatar.
3. Export (API) → кладём рядом со скриптом, указываем `COMFY_SCRIPT_NODE_ID`.
4. Ставим cron → завод работает без тебя.
