FROM python:3.10-slim-buster

WORKDIR /app

# 1. Najprej posodobite seznam paketov z zanesljivim mirrorjem
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    apt-get update || true

# 2. Namestite odvisnosti s poskusom nadaljevanja ob delnih napakah
RUN apt-get install -y --no-install-recommends --allow-unauthenticated \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "avto_vin_obd_projekt.wsgi:application", "--bind", "0.0.0.0:$PORT"]