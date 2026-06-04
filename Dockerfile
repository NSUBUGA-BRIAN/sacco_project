FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project
COPY . /app
WORKDIR /app/sacco_project

# Collect static at build (best-effort; may be re-run at runtime)
RUN python manage.py collectstatic --noinput || true

# Add start script
COPY start.sh /app/sacco_project/start.sh
RUN chmod +x /app/sacco_project/start.sh

EXPOSE 8000

CMD ["/bin/bash", "/app/sacco_project/start.sh"]
