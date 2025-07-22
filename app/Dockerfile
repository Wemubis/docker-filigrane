FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/cleanup.sh
RUN crontab /app/crontab.txt

CMD ["sh", "-c", "cron && python app.py"]

