FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    gettext \ 
    && rm -rf /var/lib/apt/lists/*


RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN pip install poetry

RUN poetry --version

WORKDIR /app

COPY . .

COPY ./src/config/config.ini /app/config.ini

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

RUN poetry install --no-root

RUN ls -al /app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]



CMD ["poetry", "run", "python", "app.py"]