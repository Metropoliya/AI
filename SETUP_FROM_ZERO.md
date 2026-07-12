# ara_studio Content Factory — Полная инструкция с нуля

> Этот файл самодостаточный. Агент, который НЕ видит исходную сессию, должен смочь
> по нему поднять весь контент-завод с нуля. Здесь: что подключить, куда идти, что
> нажать, где взять токены, как всё работает и как запустить.
> Дата: 2026-07-12. Секреты в файле — только ПЛЕЙСХОЛДЕРЫ, реальные значения не коммитим.

---

## 0. Что мы строим (за 30 секунд)

Салон **ara_studio** (Брест, владелица Александра). Нужен **автоматический контент-завод**:
1. AI генерирует **рилсы с её аватаром** (её лицо + голос, русский) и **посты-картинки**.
2. Всё **само публикуется** в Telegram-канал и Instagram по расписанию.
3. Владелица только даёт доступы — руками ничего не запускает.

Схема потока:
```
Higgsfield (аватар-видео + картинки)
        │
        ▼
  файлы/URL контента
        │
        ├──► GitHub репо (хостинг картинок) ──► GitHub Actions (крон) ──► Telegram Bot API ──► Telegram-канал
        │
        └──► Metricool MCP ──► Instagram (по расписанию)
```

---

## 1. Аккаунты и сервисы, которые НУЖНО подключить

| # | Сервис | Зачем | Где брать доступ |
|---|--------|-------|------------------|
| 1 | **Higgsfield** (план ULTRA) | генерация аватар-видео и картинок | higgsfield.ai → аккаунт → API keys |
| 2 | **Telegram Bot** | постинг в канал | @BotFather → создать бота → токен |
| 3 | **Telegram-канал** | куда постим | создать канал, бота сделать админом |
| 4 | **GitHub** (репо + Actions) | хостинг + планировщик (крон) | github.com, репо `Metropoliya/AI` |
| 5 | **Claude GitHub App** | чтобы агент мог пушить в репо | github.com/apps/claude → Install |
| 6 | **Metricool** | автопостинг в Instagram | metricool.com → подключить IG-аккаунт |
| 7 | **Apify** | парсинг Instagram + транскрипция видео | apify.com → Settings → API token |
| 8 | *(опц.)* **Exa** | веб-поиск как MCP | claude.ai → Settings → Connectors |

---

## 2. Пошаговое подключение

### Шаг 1. Higgsfield (генерация контента)
1. Зайти на **higgsfield.ai**, оформить план **ULTRA** (безлимитные генерации картинок).
2. В настройках аккаунта взять **api-key** и **secret**.
3. Higgsfield подключается как **MCP-сервер** в Claude. В интерактивной Claude Code:
   `claude mcp add` — указать сервер Higgsfield и ключи. В облачной сессии он уже был подключён.
4. Проверка: инструменты `mcp__MCP_Higgsfield__*` должны появиться (generate_image,
   generate_video, show_marketing_studio и т.д.).

**Аватар владелицы (уже создан в Higgsfield):**
- Аватар «Alexandra 2» = `5c024c60-97ff-4007-acfa-853d2716faf0` ← ПРАВИЛЬНЫЙ
- Импортированное лицо-картинка = `9f513ef7-fab5-4a68-b67e-f5ed55f22466`
- НЕ использовать старый аватар Claire `04307b5e` (было «аватар не тот»).

### Шаг 2. Telegram-бот и канал
1. В Telegram открыть **@BotFather** → `/newbot` → получить **токен бота**
   (формат `1234567890:AA...`).
2. Создать канал (или взять существующий). Наш канал ID = **`-1004380165542`**.
3. **Добавить бота админом канала** (иначе постить не сможет).
4. Проверка бота: `https://api.telegram.org/bot<ТОКЕН>/getMe` — должен вернуть `ok:true`.

### Шаг 3. GitHub — репо, секрет, Actions
1. Репозиторий: **`Metropoliya/AI`** (публичный → Actions-минуты безлимитны).
2. Положить токен бота в секрет: **Repo → Settings → Secrets and variables → Actions →
   New repository secret** → имя `TELEGRAM_BOT_TOKEN`, значение = токен из BotFather.
   ⚠️ Токен НЕЛЬЗЯ писать прямо в код/workflow — только через Secret.
3. Workflow-постер уже лежит: `.github/workflows/post-to-telegram.yml` (см. раздел 4).
4. Запуск: вкладка **Actions** → выбрать workflow → **Run workflow** (ручной),
   плюс он идёт сам по крону.

### Шаг 4. Claude GitHub App (чтобы агент пушил сам)
1. Зайти на **github.com/apps/claude** → **Install** → выбрать репо `Metropoliya/AI`.
2. После установки агент может делать `git push` и GitHub-write в этот репо.

### Шаг 5. Metricool (Instagram-автопостинг)
1. Зарегистрироваться на **metricool.com**, подключить нужный Instagram-аккаунт(ы).
2. Metricool подключается как MCP. Инструменты: `getBrandSettings` (взять `blogId`),
   `createScheduledPost` (info-JSON: providers/publicationDate/media/text), `getScheduledPosts`.

### Шаг 6. Apify (парсинг и транскрипция)
1. **apify.com** → Settings → Integrations → **API token** (формат `apify_api_...`).
2. Используется через REST (`https://api.apify.com`):
   - Парсинг Instagram: актор `apify~instagram-scraper`.
   - Транскрипция видео: актор `truefetch~video-to-text` (вход `video_url`;
     ответ item с ключом **`transcript`** = {language,text,segments}).
   - На FREE-плане лимит памяти 16GB → запускать актора ПОСЛЕДОВАТЕЛЬНО с `?memory=2048`,
     иначе ошибка `actor-memory-limit-exceeded`.

### Шаг 7. (опционально) Exa web-search
- claude.ai → **Settings → Connectors** → найти **Exa** → Connect (OAuth).
- Остальные MCP из «того видео» (Firecrawl/Playwright/Chrome/image-gen) — конфиг-MCP,
  ставятся только в десктопной Claude Code и салону избыточны.

---

## 3. Главный рецепт: рил с аватаром

Инструмент `mcp__MCP_Higgsfield__generate_video`:
```
model:          marketing_studio_video
aspect_ratio:   9:16
duration:       12
generate_audio: true
mode:           ugc_direct_to_camera
medias:         [{ role: "image", value: "9f513ef7-fab5-4a68-b67e-f5ed55f22466" }]
prompt:         на видео она говорит: <РУССКИЙ СКРИПТ> <<<avatar:5c024c60-97ff-4007-acfa-853d2716faf0>>>
```
Правила:
- Только чистые рилсы Marketing Studio. **НЕ** монтаж ffmpeg, **НЕ** Shorts Studio/restyle
  (портит лицо; владелица дважды отвергла монтаж).
- Картинки: `generate_image`, модель `seedream_v4_5` (3:4) или `nano_banana`.

---

## 4. Постер Telegram (GitHub Actions) — как устроен

Файл `.github/workflows/post-to-telegram.yml` на ветке **`main`** (крон читается только с
дефолтной ветки!). Логика:
```yaml
on:
  workflow_dispatch:        # кнопка Run workflow
  schedule:
    - cron: '0 9 * * *'     # ежедневно 09:00 UTC (12:00 Брест)
jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - env: { TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }} }
        run: |
          python3 -> Telegram Bot API sendVideo/sendPhoto, chat_id=-1004380165542
```
Важные факты:
- **Крон GitHub НЕнадёжен на коротких интервалах** (`*/5` реально срабатывает ~раз в час).
  Для 3×/день — нормально.
- Картинки хостятся прямо в репо (`images/post0..5.jpg`) и отдаются по
  `https://raw.githubusercontent.com/Metropoliya/AI/<SHA>/images/postN.jpg`.
- Токен — ТОЛЬКО из `secrets.TELEGRAM_BOT_TOKEN` (инлайн в код блокирует классификатор).

Постинг в Instagram — через Metricool MCP (`createScheduledPost`), не через Actions.

---

## 5. Текстовый оверлей на картинках

- ffmpeg на борту (imageio-ffmpeg) умеет xfade/zoompan/overlay, но **НЕ drawtext**.
- Текст кладём **Pillow** (кириллица — шрифт `DejaVuSans-Bold`). Скрипты-образцы в scratchpad:
  `overlay.py` (одна картинка), `batch_overlay.py` (пачкой).
- Формула поста: нижний тёмный градиент + заголовок в 2 строки + «ara studio · Брест» +
  «плашка» с «Запись — в директ».

---

## 6. Скиллы (37 установлено, все активны)

В `.claude/skills/` на ветке `claude/content-factory-setup-i3hoa7`:
- **council** — `github.com/unhingged/council` (совет из 5 советников + председатель).
- **36 навыков** — `github.com/aiaiohhh/claude-skills-library` (Marketing Skills Library
  от Cary Hynes: копирайтинг, реклама, CRO, SEO, контент-стратегия, лендинги, email...).

Как ставить скилл: скопировать папку `skills/<name>` из репо-источника в `.claude/skills/<name>`,
закоммитить, запушить. Claude Code грузит их при старте.

⚠️ Безопасность: внешний код скиллов ставим ТОЛЬКО когда пользователь называет конкретный
репозиторий-источник. Нельзя самому менять permissions или массово убивать Apify-раны.

---

## 7. Сеть облачной песочницы (окружение `content-factory-net`)

- РАЗРЕШЕНО: api.telegram.org, *.cloudfront.net, instagram.com / *.instagram.com /
  *.cdninstagram.com, api.apify.com + github/githubusercontent/pypi/npm.
- ЗАБЛОКИРОВАНО: huggingface.co, upload.higgsfield.ai, openaipublic.azureedge.net,
  alphacephei.com, n8n cloud.
- Прокси `http://127.0.0.1:33231`, CA `/root/.ccr/ca-bundle.crt`.
- **Playwright/Chromium прокси не проходит** (ERR_CONNECTION_RESET) → браузером парсить
  нельзя, использовать Apify.
- Если нужен новый домен — владелица добавляет его в network policy окружения.

---

## 8. Секреты — где лежат (в репо НЕ хранятся)

| Секрет | Где хранить/брать |
|--------|-------------------|
| `TELEGRAM_BOT_TOKEN` | GitHub → Settings → Secrets → Actions |
| Apify API token | apify.com → Settings; передать агенту в чате |
| Higgsfield api-key + secret | higgsfield.ai аккаунт; в конфиг MCP |
| GitHub доступ | через установленный Claude GitHub App (PAT не нужен) |

Новому агенту: НИКОГДА не коммить токены в файлы/код. Брать из GitHub Secrets или спросить владелицу.

---

## 9. Что уже сделано (чек-лист состояния на 2026-07-12)

- [x] Higgsfield подключён, аватар создан и одобрен (рил `b4ed491c`).
- [x] Telegram-бот + канал `-1004380165542`, бот админ, секрет в GitHub.
- [x] GitHub Actions постер на `main` — идёт по крону, статусы success.
- [x] 6 картинок-постов с оверлеем в репо (`images/post0..5.jpg`).
- [x] Metricool подключён, посты в Instagram планируются.
- [x] Apify: парсинг + транскрипция работают.
- [x] 37 скиллов установлены и активны.
- [x] Память проекта: `CONTENT_FACTORY_MEMORY.md`, `CLAUDE.md`.
- [ ] **Автопилот рилсов** (сам генерит+постит) — СЛОМАН: в авто-сессии Higgsfield-коннектор
      был выключен (`enabledInChat:false`). Починка: включить Higgsfield MCP в авто-сессии.
      Routine-триггер `trig_01BehmLemamyKQrKUipe5kfR` (мин. интервал крона в Routines — час).
- [ ] codegraph / Jobs-To-Be-Done / Web-Asset / Explain-Code — ждут явных ссылок на репо.

---

## 10. Ветки и файлы

- Ветка разработки: **`claude/content-factory-setup-i3hoa7`**.
- Деплой-постер: **`main`** (Actions читает крон только с дефолтной ветки).
- Ключевые файлы:
  - `.github/workflows/post-to-telegram.yml` — постер.
  - `images/post0..5.jpg` — картинки-посты.
  - `.claude/skills/` — 37 скиллов.
  - `CONTENT_FACTORY_MEMORY.md` — полная память.
  - `CLAUDE.md` — точка входа (авто-загрузка).
  - `SETUP_FROM_ZERO.md` — этот файл.

---

## 11. Быстрый старт для нового агента

1. Прочитать `CLAUDE.md` → `CONTENT_FACTORY_MEMORY.md` → этот файл.
2. Убедиться, что подключены: Higgsfield MCP, Metricool MCP, GitHub (Claude App), Apify token.
3. Взять недостающие токены из GitHub Secrets или у владелицы (НЕ коммитить).
4. Генерить рил рецептом из раздела 3; картинки — `generate_image`.
5. Постинг Telegram — через уже готовый Actions (Run workflow / крон); Instagram — Metricool.
6. Приоритетная незакрытая задача: **починить автопилот рилсов** (раздел 9).
