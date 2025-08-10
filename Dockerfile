# Uporabite Python 3.10 slim, ki je lažja različica
FROM python:3.10-slim-buster

# 1. Posodobite repozitorije in namestite orodja
# Dodani ukazi 'sed' za uporabo arhiviranih repozitorijev, kar prepreči napake
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Določite delovni imenik v vsebniku
WORKDIR /app

# 2. Namestitev Python paketov
# Kopirajte requirements.txt v delovni imenik
COPY requirements.txt .

# Namestite pakete iz requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Kopirajte celoten projekt v vsebnik
COPY . .

# 4. Omogočite izvajanje zagonske skripte in nastavite zagonski ukaz
# Naredite start.sh izvršljivo
RUN chmod +x start.sh

# ENTRYPOINT zagotovi, da se start.sh vedno izvede ob zagonu vsebnika
ENTRYPOINT ["/bin/bash", "start.sh"]

# Izpostavite port, na katerem bo delovala aplikacija
EXPOSE 8000