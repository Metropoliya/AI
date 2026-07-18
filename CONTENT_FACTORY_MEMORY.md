# ara_studio — Content Factory · Memory / Handoff

> Файл-память для любого следующего агента (Claude Code, OpenClaude и т.п.).
> Прочитай его целиком перед работой. Секретов здесь НЕТ — где лежат токены, см. раздел «Секреты».
> Последнее обновление: 2026-07-12.

---

## 1. Что это за проект

Полностью автоматический «контент-завод» для салона красоты/волос **ara_studio**
(г. Брест, владелица — Александра / Alexandra). Цель владелицы дословно:
**«100% автоматизация, без моего участия»**. Она готова *давать доступы*, но не
хочет ничего запускать руками.

Завод производит:
- **Рилсы с AI-аватаром** (её лицо/голос, русский язык) — через Higgsfield Marketing Studio.
- **Посты-картинки** салона с текстовым оверлеем.
- Публикация: **Telegram-канал `-1004380165542`** и **Instagram** (через Metricool).

---

## 2. Текущее состояние (что РАБОТАЕТ)

| Компонент | Статус | Как |
|---|---|---|
| Постинг картинок в Telegram | ✅ РАБОТАЕТ сам | GitHub Actions по крону, ветка `main` |
| Генерация рилсов (аватар) | ✅ вручную из сессии | Higgsfield MCP, аватар «Alexandra 2» |
| Постинг в Instagram | ✅ настроено | Metricool MCP (createScheduledPost) |
| Парсинг/транскрипция | ✅ | Apify REST API |
| Автопилот рилсов (сам генерит+постит) | ⚠️ СЛОМАН | см. раздел «Известные проблемы» |
| 37 скиллов | ✅ установлены и активны | `.claude/skills/` в ветке фичи |

**Проверка живости завода:** GitHub Actions `post-to-telegram.yml` на `main`
запускается по расписанию и стабильно завершается success (последние scheduled-прогоны
07-11 15:37 и 20:05 UTC — оба success).

---

## 3. Главный рабочий рецепт: рил с аватаром (Higgsfield Marketing Studio)

Инструмент: `mcp__MCP_Higgsfield__generate_video`
- model: `marketing_studio_video`
- aspect_ratio: `"9:16"`
- duration: `12`
- generate_audio: `true`
- mode: `"ugc_direct_to_camera"`
- medias: `[{role:"image", value:"<image-id лица аватара>"}]`
- prompt: `на видео она говорит: <РУССКИЙ СКРИПТ> <<<avatar:5c024c60-97ff-4007-acfa-853d2716faf0>>>`

**Ключевые ID:**
- Аватар (правильный!) = **Alexandra 2** = `5c024c60-97ff-4007-acfa-853d2716faf0`
- Импортированное лицо-картинка = `9f513ef7-fab5-4a68-b67e-f5ed55f22466`
- Одобренный владелицей рил = `b4ed491c`

**НЕ использовать:** аватар Claire `04307b5e` + ref `433d04c6` — это было «аватар не тот».
**НЕ использовать:** Shorts Studio / restyle / ffmpeg-монтаж с переходами — владелица
дважды отвергла монтаж («гавно»), Shorts Studio портит лицо. Только чистые рилсы Marketing Studio.

Картинки: `generate_image`, модели `seedream_v4_5` (использовалась, 3:4), `nano_banana` и др.
На плане ULTRA генерации безлимитны.

---

## 4. Постинг

### Telegram (напрямую, надёжно)
`.github/workflows/post-to-telegram.yml` (ветка `main`) — единственный деплой-постер.
- Постит через Telegram Bot API (`sendVideo` для рилсов / `sendPhoto` для картинок).
- CHAT = `-1004380165542`.
- Токен берётся из GitHub Secret `TELEGRAM_BOT_TOKEN` (НЕ инлайнить в код — классификатор блокирует).
- Крон: сейчас `0 9 * * *`. История менялась: рилсы → текст каждые 5 мин → картинки 3×/день.
- **Важно про GitHub cron:** для коротких интервалов (`*/5`) НЕнадёжен — реально
  срабатывает ~раз в час. Для 3×/день нормально. Публичный репо = безлимитные Actions-минуты.
- Картинки хостятся прямо в репо (`images/post0..5.jpg`) и отдаются по raw.githubusercontent URL.

### Instagram — через Metricool MCP
- `getBrandSettings` → берём `blogId`.
- `createScheduledPost` с `info` JSON: providers / publicationDate / media / text.
- `getScheduledPosts` — проверка.
- Альтернатива для нескольких аккаунтов НЕ найдена как one-click; Metricool — рабочий путь.

---

## 5. Инструменты / доступы (MCP и API)

- **Higgsfield MCP** — генерация image/video/audio, аватары (`show_marketing_studio`),
  `media_import_url`, `models_explore`, `show_plans_and_credits`, `balance`.
- **Metricool MCP** — планирование постов в Instagram.
- **Apify REST** (`api.apify.com` разрешён):
  - `apify~instagram-scraper` — парсинг профилей/рилсов.
  - `truefetch~video-to-text` — транскрипция (вход `video_url`; ответ item с ключом
    **`transcript`** = {language,text,segments}). FREE план 16GB → запускать ПОСЛЕДОВАТЕЛЬНО
    с `?memory=2048`, иначе `actor-memory-limit-exceeded`.
- **GitHub MCP** — repo-scoped на `Metropoliya/ai` (другие репо читать нельзя, но
  `search_repositories`/`search_code` работают кросс-репо). Push и GitHub-write работают
  после установки **Claude GitHub App** (github.com/apps/claude).
- **Claude Code Remote MCP** — Routines/триггеры: `create_trigger` (мин. интервал — ЧАС),
  `fire_trigger`, `send_later` (само-пробуждение, переживает рестарт контейнера).
- **n8n MCP** — требует OAuth-авторизации (в этой сессии недоступен).

### Сеть песочницы (окружение `content-factory-net`)
- РАЗРЕШЕНО: api.telegram.org, *.cloudfront.net, instagram.com/*.instagram.com/*.cdninstagram.com,
  api.apify.com + дефолты (github, githubusercontent, pypi, npm).
- ЗАБЛОКИРОВАНО: huggingface.co, upload.higgsfield.ai, openaipublic.azureedge.net,
  alphacephei.com, n8n cloud.
- Прокси: `http://127.0.0.1:33231`, CA-бандл `/root/.ccr/ca-bundle.crt`.
- Playwright/Chromium на `/opt/pw-browsers/...` — НЕ проходит прокси (ERR_CONNECTION_RESET
  на всех https). Браузером парсить нельзя — использовать Apify.

---

## 6. Скиллы (установлено 37, все активны)

В `.claude/skills/` на ветке `claude/content-factory-setup-i3hoa7`:
- **council** — из `github.com/unhingged/council` (5 советников + председатель, идея Карпатого).
- **36 навыков** из `github.com/aiaiohhh/claude-skills-library` — «Marketing Skills Library»
  (Cary Hynes): копирайтинг, реклама, CRO, SEO, контент-стратегия, лендинги, email и т.д.
  (полный список — папки в `.claude/skills/`).

Это **вся библиотека, которую продвигал изученный аккаунт @mcdenil** (Instagram-рил
`DaXQwY9Ai6P`). Транскрипции его видео сохранены в контексте: он рекламировал
Find Skills (auto-skill-finder), LLM Council, Marketing Skills Library,
Web Asset Generation, Jobs To Be Done, Explain Code (офиц. Anthropic), Deep Research,
и 5 MCP (web-search, Playwright, Firecrawl, image-gen, Chrome).

**Ограничение безопасности (классификатор):** внешний код скиллов с GitHub ставится
ТОЛЬКО когда пользователь НАЗЫВАЕТ конкретный репозиторий. Нельзя: самому менять
permissions (`.claude/settings.local.json`), массово убивать Apify-раны по статусу.

---

## 7. Не доделано / ждёт решения владелицы

- **codegraph** = `github.com/colbymchenry/codegraph` (найден, 59K⭐) — НЕ поставлен:
  нужно, чтобы владелица явно назвала этот репо. Это dev-инструмент (индекс кода),
  салону по сути не нужен.
- **Jobs To Be Done / Web Asset Generation / Explain Code** — точные репо не найдены,
  нужны ссылки (из DM @mcdenil) или явное имя репо.
- **5 MCP из видео**: только **Exa** (web-search) ставится в 1 клик как коннектор
  в claude.ai (Settings → Connectors; OAuth должна нажать сама владелица). Firecrawl /
  Playwright / Chrome / image-gen — конфиг-MCP, ставятся только в десктопной Claude Code,
  не из облачной сессии. Для салона по сути избыточны (Higgsfield=image-gen, Apify=парсинг).

---

## 7.5. ГОЛОС АВАТАРА — итоги экспериментов 2026-07-18 (ВАЖНО)

Проблема: родная озвучка Marketing Studio говорит по-русски С АКЦЕНТОМ («как иностранка»).

Что проверено и НЕ работает:
- `voice_change` поверх MS-видео — коверкает русский (транскрипция выдаёт кашу). ❌
- `dubbing` (rus→rus) — липсинк ок, но пересинтез даёт ШОРОХ-хвосты после слов;
  шумодав+гейт (ffmpeg afftdn+agate) снижают, но не убирают полностью. ❌
- Seedance 2.0 с audio_references — губы НЕ попадают. ❌

Что РАБОТАЕТ (текущий лучший рецепт рила):
1. Озвучка: `generate_audio` model=`text2speech_v2`, variant=`elevenlabs`,
   voice_type=`element`, voice_id=`6e3ace60-8316-4f32-82c4-630bec0902f2` («Александра-3»,
   клон голоса владелицы). Чистый русский без акцента (проверено транскрипцией).
2. Кадр: фото аватара → `outpaint_image` до 9:16 (иначе видео унаследует пропорции фото).
3. Видео: `generate_video` model=`wan2_7`, medias: start_image=аутпейнт-фото,
   audio_references=TTS-job. В промпте: живая ручная камера (push-in, дрейф), жестикуляция.
   Wan вшивает РЕФЕРЕНСНОЕ аудио без пересинтеза (корреляция 1.000) и синкает губы. ✅
4. Проверка ПЕРЕД отправкой (обязательна): ffmpeg-стримы (есть ли звук!), корреляция
   аудио с оригиналом, сетка кадров fps=1 (гримасы/статичность ловятся только так).

Новый аватар из свежих фото владелицы: «Alexandra 3 (ara_studio)» =
`0903d7cd-7bab-4fb1-8764-8b878cf30a34` (лицо-фото `0a56d8b7-910a-40f9-8172-d74a5dcfbc54`,
аутпейнт 9:16 = job `0c4db37d-8847-466b-bf42-090f0b572e79`).
Голос К АВАТАРУ в UI Higgsfield привязать НЕЛЬЗЯ (проверено владелицей — опции нет).
Голосовые клоны в аккаунте: «Александра-3» `6e3ace60…` и «Александра-1»=«мой-голос-1»
`438ba3ef…` (одинаковый образец).

⚠️ Apify: месячная квота FREE-плана ИСЧЕРПАНА (2026-07-18) — транскрипция недоступна
до апгрейда. Замена: `video_analysis_create` в Higgsfield (посценная расшифровка речи).

### Итоги deep-research по реалистичному голосу (2026-07-18, 22 проверенных факта)
- Клон голоса в Higgsfield рендерится через 5 движков, движок выбирается НА КАЖДУЮ
  генерацию: `text2speech_v2` + variant = elevenlabs (дефолт) | minimax (рекомендован
  для цифровых двойников) | seed_speech (с клоном-element даёт 400) | vibe_voice | cozy_voice.
- A/B-тест отправлен владелице: golos_1_elevenlabs.mp3 vs golos_2_minimax.mp3
  (какой движок выбрала — СПРОСИТЬ, на 2026-07-18 ответа ещё нет).
- Самый большой прирост реализма — НОВЫЙ образец записи: 1.5–2 мин живой речи в тихой
  комнате → новый клон (create_voice; лимит ~3 клона на аккаунт, старый удалить).
- Живость подачи — разметкой текста промпта: ЗАГЛАВНЫЕ=акцент, «…»=пауза,
  [смеётся]/[шёпотом]=эмоции, длинные промпты естественнее (официальные приёмы Speak 2.0).
- Русский на страницах Higgsfield явно не назван (только «74+ языков») → надёжный маршрут:
  клон → готовое аудио → липсинк (Wan 2.7 / Lipsync Studio), НЕ промпт-генерация речи видеомоделью.
- НЕ проверено (лимиты выборки): ElevenLabs Professional Voice Clone напрямую, HeyGen,
  standalone-липсинки (sync.so, OmniHuman) — следующий рубеж, если текущее не устроит.
- Финальный одобряемый рил сессии: final2.mp4 = job `a353bc7a` (Wan 2.7, живая камера,
  чистый EL-звук). Вердикта владелицы на 2026-07-18 нет — СПРОСИТЬ.

## 8. Известные проблемы / уроки

- **Автопилот рилсов сломан:** Routine `trig_01BehmLemamyKQrKUipe5kfR` срабатывал, но в
  свежей авто-сессии Higgsfield-коннектор `enabledInChat: false` → генерация не шла
  (Telegram getMe при этом ок). Чтобы починить: в авто-сессии должен быть включён
  Higgsfield MCP. Токены в триггер инлайнить нельзя (классификатор) — только через env
  (`$TELEGRAM_BOT_TOKEN`).
- Монтаж ffmpeg (xfade/zoompan/overlay есть, drawtext НЕТ) — отвергнут. Текст на картинки
  кладём через Pillow (кириллица: DejaVuSans-Bold). Скрипты: scratchpad
  `overlay.py`, `batch_overlay.py`.
- `upload.higgsfield.ai` 403 → готовые картинки хостим через git push в репо.
- Транскрипция: HuggingFace/Azure/vosk заблокированы → только Apify `truefetch~video-to-text`.

---

## 9. Секреты (В РЕПО НЕ ХРАНЯТСЯ — только указатели)

Реальные значения — в чате сессии и/или GitHub Secrets. Никогда не коммить в репо/файлы:
- `TELEGRAM_BOT_TOKEN` — есть в GitHub → Settings → Secrets (используется workflow’ом).
- Apify token — давала владелица в чате.
- Higgsfield api-key + secret — в чате.
- GitHub PAT — был выдан, через прокси не работает, лучше удалить.

Новому агенту: запроси недостающие токены у владелицы или возьми из GitHub Secrets;
НЕ вписывай их в код/коммиты.

---

## 10. Ветки

- Разработка: `claude/content-factory-setup-i3hoa7` (здесь скиллы и правки).
- Деплой постера: `main` (GitHub Actions читает крон с дефолтной ветки).
