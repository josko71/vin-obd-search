# Uporabite Python 3.10 slim, ki je bolj stabilen in manjši.
# bullseye je novejša in bolj stabilna različica od busterja
FROM python:3.10-slim-bullseye

# Nastavitev delovnega direktorija
WORKDIR /app

# Nastavitev okoljskih spremenljivk
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Posodobitev repozitorijev in namestitev orodij za gradnjo in knjižnic
# apt-get clean na koncu poskrbi za čiščenje medpomnilnika
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiranje datoteke z zahtevami in namestitev odvisnosti
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiranje preostale kode
COPY . /app

# Izpostavitev porta, ki ga bo poslušala aplikacija
EXPOSE 8000

# Ukaz za zagon aplikacije
CMD ["./start.sh"]
