# Uporabimo uradno Python sliko, ki je primerna za spletne aplikacije
FROM python:3.12-slim

# Nastavimo delovni direktorij
WORKDIR /app

# Namestimo sistemske odvisnosti za mysqlclient
# To je ključni del, ki rešuje vašo težavo
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Kopiramo requirements.txt in namestimo Python odvisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo preostalo kodo
COPY . .

# Nastavimo okoljske spremenljivke
ENV DJANGO_SETTINGS_MODULE=avto_vin_obd_projekt.settings

# Zberemo statične datoteke
RUN python manage.py collectstatic --noinput

# Izpostavimo vrata, ki jih bo uporabljal vaš web strežnik (npr. gunicorn)
EXPOSE 8000

# Določimo privzeti ukaz za zagon strežnika
# To je primer za Gunicorn, ki se pogosto uporablja v produkciji
# Namestiti boste morali Gunicorn in ga dodati v requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "avto_vin_obd_projekt.wsgi:application"]