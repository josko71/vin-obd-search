# Stage 1: Build stage
FROM python:3.12-slim as build-stage

WORKDIR /app

# Namestimo sistemske odvisnosti (dodali postgresql-client)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add before collectstatic
RUN python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput

RUN python manage.py collectstatic --noinput


# Stage 2: Final stage (Runtime)
FROM python:3.12-slim

WORKDIR /app

# Namestimo postgresql-client v runtime fazi
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build-stage /app/avto_vin_obd_projekt /app/avto_vin_obd_projekt
COPY --from=build-stage /app/vozila /app/vozila
COPY --from=build-stage /app/manage.py .
COPY --from=build-stage /app/requirements.txt .
COPY --from=build-stage /app/static_root /app/static_root
COPY --from=build-stage /app/data_csv /app/data_csv

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=avto_vin_obd_projekt.settings
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "avto_vin_obd_projekt.wsgi:application"]