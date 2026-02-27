# cambiodemando - Imagen única; settings vía DJANGO_SETTINGS_MODULE en compose
FROM python:3.12-slim

# Dependencias de sistema para psycopg2-binary (por si se cambia a psycopg2 en prod)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puertos: 8000 (runserver / gunicorn)
EXPOSE 8000

# Comando por defecto (compose lo sobrescribe: runserver en dev, gunicorn en prod)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
