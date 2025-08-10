FROM python:3.10-slim-buster

# Posodobite repozitorije in namestite orodja
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Namestitev Python paketov
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Kopirajte celoten projekt
COPY . .

# Omogočite izvajanje zagonske skripte
RUN chmod +x start.sh

# Zagonski ukaz
ENTRYPOINT ["/bin/bash", "start.sh"]

EXPOSE 8000