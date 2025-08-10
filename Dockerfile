FROM python:3.10-slim-buster

# 1. Posodobite repozitorije in namestite orodja
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Namestitev Python paketov
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Kopirajte kodo in zagonsko skripto
COPY . .
RUN chmod +x start.sh

# 4. ENTRYPOINT: Zažene skripto, ki izvede migracije in zažene strežnik
ENTRYPOINT ["./start.sh"]