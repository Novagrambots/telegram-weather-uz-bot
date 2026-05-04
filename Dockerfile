FROM python:3.12-slim

# wget для healthcheck и системные утилиты
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# сначала зависимости (кэшируется Docker слоем)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# потом код + seeds
COPY bot/ bot/
COPY seeds/ seeds/
COPY alembic/ alembic/
COPY alembic.ini ./

CMD ["python", "-m", "bot.main"]
