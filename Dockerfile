FROM python:3.11-slim

WORKDIR /app

# Reflex may install Bun tooling; unzip is required in your logs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates nodejs npm unzip \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000 8000

CMD ["bash","-lc","reflex run --env prod"]
