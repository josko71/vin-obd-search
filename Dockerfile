FROM python:3.10-slim-buster  # Specifičnejša verzija za večjo zanesljivost

WORKDIR /app

# 1. Sistemske odvisnosti
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Ločena instalacija requirements za boljše caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Ločen korak za COPY . . za izkoriščanje Docker cache
COPY . .

# 4. Optimizacija za collectstatic
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python manage.py collectstatic --noinput --clear

# 5. Izboljšana Gunicorn konfiguracija
CMD ["gunicorn", "avto_vin_obd_projekt.wsgi:application", \
    "--bind", "0.0.0.0:$PORT", \
    "--workers", "4", \
    "--worker-class", "gthread", \
    "--threads", "2", \
    "--timeout", "120", \
    "--log-level", "info"]