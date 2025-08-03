# Stage 1: Build stage
# Uporabimo sliko z vsemi orodji za build
FROM python:3.12-slim as build-stage

# Nastavimo delovni direktorij
WORKDIR /app

# Namestimo sistemske odvisnosti za PostgreSQL
# Uporabimo en ukaz RUN, da zmanjšamo število slojev in počistimo cache
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiramo requirements.txt in namestimo Python odvisnosti
# To je ključen korak, da se izkoristi caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo preostalo kodo projekta
COPY . .

# Zberemo statične datoteke - to se zgodi med buildom
# Uporabimo --noinput, da se izognemo interaktivnim vprašanjem
RUN python manage.py collectstatic --noinput

# Stage 2: Final stage (Runtime)
# Uporabimo še manjšo Python sliko za končno okolje, ki ne potrebuje orodij za build
FROM python:3.12-slim

# Nastavimo delovni direktorij
WORKDIR /app

# Kopiramo samo tisto, kar je potrebno za zagon aplikacije iz prve faze
# To vključuje Python kodo, statične datoteke in manage.py
COPY --from=build-stage /app/avto_vin_obd_projekt /app/avto_vin_obd_projekt
COPY --from=build-stage /app/vozila /app/vozila
COPY --from=build-stage /app/manage.py .
COPY --from=build-stage /app/requirements.txt .

# Dodamo statične datoteke
COPY --from=build-stage /app/collected-static /app/collected-static

# Namestimo pakete za zagon - ni treba ponovno nameščati orodij za build
RUN pip install --no-cache-dir -r requirements.txt

# Nastavimo okoljske spremenljivke
ENV DJANGO_SETTINGS_MODULE=avto_vin_obd_projekt.settings

# Izpostavimo vrata, ki jih bo uporabljal vaš web strežnik (npr. gunicorn)
EXPOSE 8000

# Določimo privzeti ukaz za zagon strežnika
# Gunicorn mora biti v vašem requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "avto_vin_obd_projekt.wsgi:application"]