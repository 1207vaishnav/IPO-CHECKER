FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN python -m playwright install --with-deps chromium

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "ipo_checker.wsgi:application"]