# Dockerfile
FROM python:3.10-slim

# Установка системных зависимостей для newspaper3k и других
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка nltk и загрузка punkt
RUN pip install --upgrade pip && \
    pip install nltk && \
    python -m nltk.downloader punkt

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем все файлы проекта
COPY . /app

# Установка зависимостей
RUN pip install -r requirements.txt

# Команда запуска
CMD ["python", "bot.py"]
