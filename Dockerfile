FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m playwright install chromium

RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "gunicorn ipo_checker.wsgi:application --bind 0.0.0.0:$PORT"]