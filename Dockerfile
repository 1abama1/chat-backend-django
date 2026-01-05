FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY docker/wait-for-it.sh /app/docker/wait-for-it.sh
RUN chmod +x /app/docker/wait-for-it.sh

COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

COPY backend backend
WORKDIR /app/backend

ENV DJANGO_SETTINGS_MODULE=backend.settings

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]