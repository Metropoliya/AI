# 🏭 Контент-завод в n8n (Higgsfield → Telegram)

Автопилот: по расписанию генерирует текст рилса → озвучку твоим голосом → видео с аватаром → публикует в Telegram-канал.

Файл воркфлоу: **`content-factory-workflow.json`** (импортируй в n8n).

## Схема
```
Расписание (10:00) → Конфиг → LLM (текст+caption)
  → Higgsfield озвучка → ждать/poll
  → Higgsfield видео (wan2_7) → ждать/poll
  → Telegram sendVideo (видео + caption)
```
Циклы ожидания: если статус ещё не `completed` — нода «Ждать» и повторный запрос статуса (петля), пока не готово.

## Настройка (n8n Cloud)

### 1. Импорт
n8n → **Workflows → Import from File** → выбери `content-factory-workflow.json`.

### 2. Ключи (Credentials)
Создай в n8n → **Credentials**:
- **Higgsfield** — тип *Header Auth*: имя `Authorization`, значение `Key <api-key>:<secret>`
  (пара из `cloud.higgsfield.ai`: `Key 001fbed2-...:0e42416b...`). База API `https://platform.higgsfield.ai`.
  Тратит **те же кредиты**, что и твой аккаунт.
  ⚠️ Проверь в своём API-дашборде, какие модели доступны по REST: image2video (`POST /v1/image2video/dop`) точно есть; TTS клон-голосом и talking-avatar (Wan/speech2video) могут быть только в приложении/MCP — тогда эти шаги оставляем на app.
- **OpenAI** (или другой LLM) — тип *Header Auth*: `Authorization` = `Bearer <openai_key>` (нода «LLM: текст рилса»).
- **Telegram** — нода Telegram → Credential *Telegram API* → вставь токен бота `@BotFather`.

Привяжи эти credentials к соответствующим нодам (HTTP-ноды Higgsfield → Higgsfield cred; LLM-нода → OpenAI cred; Telegram-нода → Telegram cred).

### 3. «Ключи завода» (уже вписаны в ноду «Конфиг завода»)
- `avatar_media_id` = `fa4b5e1e-0cf8-451f-9fbb-92ea36de09b1` — твой зафиксированный аватар
- `voice_id` = `438ba3ef-da19-43ee-aa02-7d3a21a974a4` — голос «Александра-1»
- `chat_id` = `-1004380165542` — твой канал
- `topic` — тема дня (можно сделать список/ротацию)

### 4. ⚠️ Сверить эндпоинты Higgsfield
В HTTP-нодах Higgsfield URL и поля тела проставлены по схеме параметров MCP как заготовка:
- `POST /v1/audio/generations` (озвучка), `POST /v1/video/generations` (видео), `GET /v1/jobs/{id}` (статус) — база `https://platform.higgsfield.ai`.

**Точные путь/поля возьми из своей API-документации Higgsfield** (после выпуска ключа) и поправь URL/JSON в 4 нодах: «Higgsfield: озвучка», «Статус аудио», «Higgsfield: видео wan2_7», «Статус видео». Тело запросов совпадает с параметрами, которые мы использовали (`model`, `voice_id`, `medias[role/value]` и т.д.).

### 5. Проверка
- Открой воркфлоу → **Execute Workflow** (ручной прогон).
- Пройди по нодам: текст → аудио готово → видео готово → пост ушёл в канал.
- Как всё зелёное — включи тумблер **Active** (пойдёт по расписанию).

## Идеи развития
- Список тем в Google Sheets → нода Sheets вместо статичного `topic` (ротация без правок).
- Добавить `upscale` до 1080p и субтитры перед отправкой.
- Постить не только в Telegram (Instagram/TikTok — через их API-ноды).
- Ветка «на проверку»: сначала слать видео тебе в личку, ты жмёшь 👍 — только потом в канал.
