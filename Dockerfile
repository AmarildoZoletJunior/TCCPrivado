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
RUN poetry install --no-root
EXPOSE 8000
CMD ["poetry", "run", "app.py"]