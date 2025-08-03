# Stage 1: Build stage
# Uporabimo sliko z vsemi orodji za build
FROM python:3.12-slim as build-stage

# Nastavimo delovni direktorij
WORKDIR /app

# Namestimo sistemske odvisnosti za PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiramo requirements.txt in namestimo Python odvisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo preostalo kodo projekta
COPY . .

# Zberemo statične datoteke - to se zgodi med buildom
# Uporabimo --noinput, da se izognemo interaktivnim vprašanjem
RUN python manage.py collectstatic --noinput

# Stage 2: Final stage (Runtime)
# Uporabimo še manjšo Python sliko za končno okolje
FROM python:3.12-slim

# Nastavimo delovni direktorij
WORKDIR /app

# Kopiramo samo tisto, kar je potrebno za zagon aplikacije iz prve faze
COPY --from=build-stage /app/avto_vin_obd_projekt /app/avto_vin_obd_projekt
COPY --from=build-stage /app/vozila /app/vozila
COPY --from=build-stage /app/manage.py .
COPY --from=build-stage /app/requirements.txt .

# Kopiramo zbrane statične datoteke v končno sliko
COPY --from=build-stage /app/static_root /app/static_root

# Namestimo pakete za zagon
RUN pip install --no-cache-dir -r requirements.txt

# Nastavimo okoljske spremenljivke
ENV DJANGO_SETTINGS_MODULE=avto_vin_obd_projekt.settings

# Izpostavimo vrata, ki jih bo uporabljal vaš web strežnik (npr. gunicorn)
EXPOSE 8000

# Določimo privzeti ukaz za zagon strežnika
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "avto_vin_obd_projekt.wsgi:application"]