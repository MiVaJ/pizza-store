FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для psycopg и сборки пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry==2.4.1

# Poetry не создаёт venv внутри контейнера
RUN poetry config virtualenvs.create false
ENV POETRY_VIRTUALENVS_CREATE=false

# Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

# Копируем остальной код
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]