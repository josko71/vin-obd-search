FROM python:3.10-slim-buster

# 1. Posodobite repozitorije in namestite osnovna orodja
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Namestitev Python paketov
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install alembic==1.13.3 && \  # Namesto dev verzije
RUN pip install --no-cache-dir -r requirements.txt --ignore-installed alembic

COPY . .

CMD ["gunicorn", "avto_vin_obd_projekt.wsgi:application", "--bind", "0.0.0.0:$PORT"]RT"]