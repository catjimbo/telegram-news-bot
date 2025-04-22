import asyncio
import nest_asyncio
import logging
import os
import feedparser
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from transformers import pipeline
from openai import OpenAI
import newspaper
from database import init_db, get_user_tags, set_user_tags

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Zero-shot классификатор
classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    tokenizer="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
)

# OpenAI клиент
client = OpenAI(api_key=OPENAI_API_KEY)

# Список источников новостей
RSS_SOURCES = [
    "https://lenta.ru/rss/news",
    "https://ria.ru/export/rss2/world/index.xml",
    "https://www.vedomosti.ru/rss/news",
    "https://tass.ru/rss/v2.xml"
]


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я умный новостной бот 🤖\n\n"
        "1. Напиши /subscribe <теги> — например: /subscribe космос, технологии\n"
        "2. Потом — /news, чтобы получить подборку новостей по твоим темам 🗞️"
    )

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.args:
        tags = ' '.join(context.args).split(',')
        tags = [tag.strip().lower() for tag in tags]
        await set_user_tags(user_id, tags)
        await update.message.reply_text(f"Темы сохранены: {', '.join(tags)}")
    else:
        await update.message.reply_text("Пожалуйста, укажи темы через запятую. Пример: /subscribe ИИ, космос")

# Команда /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tags = await get_user_tags(user_id)

    if not tags:
        await update.message.reply_text("Ты пока не выбрал темы. Напиши /subscribe <теги>")
        return

    matched = []
    max_checked = 100  # ограничим количество проверок
    checked = 0

    for url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if checked >= max_checked or len(matched) >= 5:
                break
            if is_relevant_zero_shot(entry, tags):
                matched.append(entry)
            checked += 1

    if not matched:
        await update.message.reply_text("Не нашёл новостей по твоим темам 😕")
        return

    for entry in matched:
        summary = await summarize(entry)
        message = f"📰 {entry.title}\n\n📝 {summary}\n\n🔗 {entry.link}"
        await update.message.reply_text(message)

# Zero-shot фильтрация

def is_relevant_zero_shot(entry, tags, threshold=0.8):
    title = getattr(entry, "title", "")
    description = getattr(entry, "description", "")
    summary = getattr(entry, "summary", "")
    content = ""

    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].value

    text = f"{title}. {description} {summary} {content}".strip().replace('\n', ' ')

    if not text or not tags:
        return False

    try:
        result = classifier(text, candidate_labels=tags)
        top_score = result["scores"][0]
        top_label = result["labels"][0]

        print(f"[Zero-Shot] '{title}' → {top_label} ({top_score:.2f})")
        return top_score >= threshold
    except Exception as e:
        print(f"[Zero-Shot] Ошибка: {e}")
        return False

# Получение полного текста статьи

def extract_article_text(url):
    try:
        article = newspaper.Article(url, language="ru")
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Ошибка при загрузке статьи: {e}")
        return ""

# Генерация саммари через ChatGPT
async def summarize(entry) -> str:
    article_text = extract_article_text(entry.link)
    title = getattr(entry, "title", "")
    fallback = f"{title}. {getattr(entry, 'description', '')}"
    text = article_text if article_text else fallback

    prompt = (
        "Ты — ассистент, делающий саммари новостей."
        " Сформулируй краткое саммари:\n\n"
        f"{text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT Summary] Ошибка: {e}")
        return "(Не удалось сгенерировать саммари)"

# Запуск бота
async def main():
    await init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("news", news))
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
