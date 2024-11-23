FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry --version

WORKDIR /app

COPY . .

COPY ./src/config/config.ini /app/config.ini

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

RUN poetry install --no-root

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["poetry", "run", "app.py"]