# CLAUDE.md

Проект: **контент-завод ara_studio** (салон красоты, Брест, владелица Александра).
Цель — 100% автоматическая генерация и публикация контента (рилсы с AI-аватаром +
посты-картинки) в Telegram-канал `-1004380165542` и Instagram, без участия владелицы.

## 📌 Прочитай перед работой
- **Инструкция с НУЛЯ (что подключить, куда идти, что нажать) → [`SETUP_FROM_ZERO.md`](./SETUP_FROM_ZERO.md).**
- **Полная память проекта (рецепты, ID, доступы, проблемы) → [`CONTENT_FACTORY_MEMORY.md`](./CONTENT_FACTORY_MEMORY.md).**

Кратко:
- Рилсы: Higgsfield Marketing Studio, аватар `5c024c60-97ff-4007-acfa-853d2716faf0`.
- Постинг: GitHub Actions `.github/workflows/post-to-telegram.yml` (ветка `main`, по крону).
- Instagram: Metricool MCP. Парсинг/транскрипция: Apify REST.
- Ветка разработки: `claude/content-factory-setup-i3hoa7`.
- Секреты в репо НЕ хранить — токены в GitHub Secrets / чате.
