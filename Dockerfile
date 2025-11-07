FROM python:3.13-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional libpq-dev build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]