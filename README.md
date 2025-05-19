# 🤖 Telegram News Bot

Интеллектуальный Telegram-бот, который собирает новости из различных источников (RSS) по заданным пользователем темам, фильтрует их с помощью языковой модели (Zero-Shot), и выдаёт краткие саммари с помощью OpenAI GPT.

---

## 📦 Возможности

- Команды:
  - `/start` — приветствие
  - `/subscribe <теги>` — подписка на темы (например: `/subscribe технологии, космос`)
  - `/news` — получение актуальных новостей по темам

- Поддержка тегов пользователя (RSS + AI-фильтрация)
- Подключение языковой модели (zero-shot classification)
- Саммари статей через OpenAI (ChatGPT)
- Агрегация новостей из RSS-источников
- Docker-контейнер для развёртывания

---

## ⚙️ Используемые технологии

- Python 3.10+
- `python-telegram-bot`
- `feedparser`, `newspaper3k`
- `transformers`, `torch`, `nltk`
- `OpenAI API`
- `dotenv`, `sqlite`
- Docker 🐳

---

## 🚀 Быстрый запуск (через Docker)

### 1. Клонируй проект

```bash
git clone https://github.com/your-username/telegram-news-bot.git
cd telegram-news-bot
```

### 2. Подготовь `.env` файл

Создай `.env` рядом с `bot.py`:

```
TELEGRAM_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_api_key
```

### 3. Собери и запусти бота

```bash
docker compose up -d --build
```

Бот начнёт работать в фоне, все данные будут сохраняться в `./data/bot.db`

### 4. Просмотр логов

```bash
docker logs -f telegram-news-bot
```

---

## 📁 Структура проекта

```
├── bot.py              # Основной Telegram-бот
├── database.py         # Работа с SQLite (если есть)
├── Dockerfile          # Сборка образа
├── docker-compose.yml  # Запуск сервиса
├── requirements.txt    # Зависимости Python
├── .env.example        # Пример файла окружения
├── data/               # База данных SQLite (монтируется)
└── README.md           # Документация
```

---

## 📮 Источники новостей (по умолчанию)

- [Lenta.ru](https://lenta.ru/rss/news)
- [РИА Новости](https://ria.ru/export/rss2/world/index.xml)
- [Ведомости](https://www.vedomosti.ru/rss/news)
- [ТАСС](https://tass.ru/rss/v2.xml)

---

## 🧠 Roadmap (по желанию)

- [ ] Добавить фильтрацию фейковых новостей
- [ ] Хранение пользователей и тем в БД
- [ ] Панель администратора
- [ ] Расширенные источники (через API)
