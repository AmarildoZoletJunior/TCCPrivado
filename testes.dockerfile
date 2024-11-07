# Use a imagem oficial do Python
FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Adicionar o Poetry ao PATH
ENV PATH="$HOME/.poetry/bin:$PATH"

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo do projeto para o contêiner
COPY . .

# Instalar dependências do Poetry
RUN poetry install --no-root

EXPOSE 8000

CMD ["poetry", "run", "pytest"]
