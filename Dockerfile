FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# compilemessages needs gettext (msgfmt)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py compilemessages
RUN python manage.py collectstatic --noinput

EXPOSE 8001
CMD ["gunicorn", "lingolist.wsgi:application", "--bind", "0.0.0.0:8001"]
