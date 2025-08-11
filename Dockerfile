# Uporabite bolj stabilno osnovno sliko
FROM python:3.10-slim-buster

# Nastavitev delovnega direktorija
WORKDIR /app

# Posodobite repozitorije in namestite orodja
# Poskusite s preprostejšim ukazom in preverite, ali odpravi napako
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*