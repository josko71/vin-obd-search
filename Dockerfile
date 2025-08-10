FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]